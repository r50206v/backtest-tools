from bt.algos import SelectWhere, WeighTarget
import pandas as pd
import numpy as np
import importlib
from backtest_tools.helper import _check_params, _valid_id, _convert_type
from backtest_tools.exceptions import RequirementNotMeetException


def weigh_target(data_table, params):
    '''
    params (list of dict):
        {
            'action': [
                {
                    'indicator_id': 3,
                    'method': ooo,
                    'asset_id': x,
                    'strategy': x,
                    'params': {
                        parameters for method
                    }
                }, {...}
            ]
        }
    '''
    _check_params(params, ['action'])
    actionList = []
    for id_params in params['action']:
        pkg = importlib.import_module('backtest_tools.backtest.customized_strategy')
        func = getattr(pkg, id_params['method'])

        dateList = func(
            data_table=data_table, 
            indicatorID=id_params['indicator_id'], 
            params=id_params['params']
        )

        if isinstance(id_params['asset_id'], (int, float)): 
            id_params['asset_id'] = str(id_params['asset_id'])
        if not isinstance(id_params['asset_id'], str):
            raise RequirementNotMeetException('asset ID should be str(preferred), int, or float')
        if id_params['strategy'] not in ['buy', 'sell', 'hold']:
            raise RequirementNotMeetException('no such strategy %s' % id_params['strategy'])
        
        action = [
            [id_params['strategy'], id_params['asset_id'], date]
            for date in dateList
        ]
        if not actionList:
            actionList = action
        else:
            # add all `buy`, `sell`, `hold` action
            # it means if any action matches the condition, then do it 
            # `buy action1` Or `buy action2` Or `sell action1` Or `hold action1`
            actionList.extend(action)

    # actionList contains [strategy, asset_id, date]
    actionList = sorted(actionList, key=lambda x: x[2])
    weight = data_table.asset.copy(deep=True)
    weight[:] = 0

    # if need `action1` And `action2` 
    # -> pd.DataFrame(actionList).groupby(2).agg(np.array)
    for action in actionList:
        if action[0] == 'buy':
            insert_value = 1
        elif action[0] == 'sell':
            insert_value = -1
        elif action[0] == 'hold':
            insert_value = 0
        else:
            raise RequirementNotMeetException('unknown action\n')
        weight.loc[action[2]:, action[1]] = insert_value

    weight.fillna(0, inplace=True)
    return WeighTarget(weights=weight)



def trade_at_threshold(data_table, indicatorID, params):
    '''
    reference: py/Strategy.py DataThreshold

    params (dict):
        {
            'threshold': x,
            'n': x,
            'sign': 1,
        }

    threshold (float): 門檻值
    n (int): 符合門檻值的連續期數
    sign (int): set([1, -1]) 做多為1，做空為-1
                若是做多平倉則為-1，做空平倉為1
    '''
    _check_params(params, ['threshold', 'n', 'sign'])
    params = _convert_type(params, ['n', 'sign'], int)
    params = _convert_type(params, ['threshold'], float)
    indicatorID = _valid_id(indicatorID)
    if indicatorID not in data_table.use_id['indicator']:
        raise RequirementNotMeetException('indicator ID %s not in Data Table\n' % indicatorID)

    indicatorDF = data_table.indicator[indicatorID]\
                            .copy(deep=True)\
                            .shift(1)

    if params['sign'] == 1:
        rolling_min = indicatorDF.rolling(
            window=params['n'], 
            center=False
        ).min()

        dateList = indicatorDF[
            (rolling_min >= params['threshold']) &
            (rolling_min.shift(1) < params['threshold'])
        ].index.values
    
    elif params['sign'] == -1:
        rolling_max = indicatorDF.rolling(
            window=params['n'], 
            center=False
        ).max()
        dateList = indicatorDF[
            (rolling_max <= params['threshold']) &
            (rolling_max.shift(1) > params['threshold'])
        ].index.values

    else: 
        raise RequirementNotMeetException('sign should be either 1 or -1\n')
    
    return dateList


def continuous_growth(data_table, indicatorID, params):
    '''
    reference: py/Strategy.py ContinuousGrowth

    params (dict):
        {
            'n': x,
            'sign': 1,
        }

    n (int): 符合門檻值的連續期數
    sign (int): set([1, -1]) 做多為1，做空為-1
                若是做多平倉則為-1，做空平倉為1
    '''
    _check_params(params, ['n', 'sign'])
    params = _convert_type(params, ['n', 'sign'], int)
    indicatorID = _valid_id(indicatorID)
    if indicatorID not in data_table.use_id['indicator']:
        raise RequirementNotMeetException('indicator ID %s not in Data Table\n' % indicatorID)
    
    indicatorDF = data_table.indicator[indicatorID]\
                            .copy(deep=True)\
                            .shift(1)
    if params['sign'] == 1:
        grow_min = indicatorDF.diff().rolling(
            window=params['n'], center=False
        ).min()
        dateList = indicatorDF[
            (grow_min >= 0) &
            (grow_min.shift(1) < 0)
        ].index.values

    elif params['sign'] == -1:
        grow_max = indicatorDF.diff().rolling(
            window=params['n'], center=False
        ).max()
        dateList = indicatorDF[
            (grow_max < 0) &
            (grow_max.shift(1) >= 0)
        ].index
    
    else: 
        raise RequirementNotMeetException('sign should be either 1 or -1\n')

    return dateList


def cumulative_return_threshold(data_table, indicatorID, params):
    '''
    reference: py/Strategy.py CumulativeReturnThreshold

    params (dict):
        {
            'threshold': x,
            'n': x,
            'sign': 1,
        }

    threshold (float): 門檻值
    n (int): 符合門檻值的連續期數
    sign (int): set([1, -1]) 做多為1，做空為-1
                若是做多平倉則為-1，做空平倉為1
    '''
    _check_params(params, ['threshold', 'n', 'sign'])
    params = _convert_type(params, ['n', 'sign'], int)
    params = _convert_type(params, ['threshold'], float)
    indicatorID = _valid_id(indicatorID)
    if indicatorID not in data_table.use_id['indicator']:
        raise RequirementNotMeetException('indicator ID %s not in Data Table\n' % indicatorID)

    indicatorDF = data_table.indicator[indicatorID]\
                            .copy(deep=True)\
                            .shift(1)

    rolling_return = indicatorDF.pct_change(params['n'])
    if params['sign'] == 1:
        dateList = indicatorDF[
            (rolling_return >= params['threshold']) &
            (rolling_return.shift(1) < params['threshold'])
        ].index.values
        
    elif params['sign'] == -1:
        dateList = indicatorDF[
            (rolling_return < params['threshold']) &
            (rolling_return.shift(1) >= params['threshold'])
        ].index.values

    else: 
        raise RequirementNotMeetException('sign should be either 1 or -1\n')

    return dateList


def specific_date(data_table, indicatorID, params):
    '''
    reference: py/Strategy.py SelfChoice

    params (dict):
        {
            'sign': 1,
            'date': [x, x, x]
        }

    date (list of datetime format): ['2018-01-01', '2018-02-01', ...]
    sign (int): set([1, -1]) 做多為1，做空為-1
                若是做多平倉則為-1，做空平倉為1
    '''
    _check_params(params, ['sign', 'date'])
    params = _convert_type(params, ['sign'], int)
    indicatorID = _valid_id(indicatorID)
    if indicatorID not in data_table.use_id['indicator']:
        raise RequirementNotMeetException('indicator ID %s not in Data Table\n' % indicatorID)
    if params['sign'] not in [1, -1]:
        raise RequirementNotMeetException('sign should be either 1 or -1\n')
    if not isinstance(params['date'], list):
        raise RequirementNotMeetException('date should be list of datetime format\n')
    
    return pd.to_datetime(params['date'], format='%Y-%m-%d').values


def ma_crossover_ma(data_table, indicatorID, params):
    '''
    params (dict):
        {
            'sign': 1,
            'ma1': 5,
            'ma2': 10
        }
    
    ma1 (int): 5
    ma2 (int): 10
    sign (int): set([1, -1]) 做多為1，做空為-1
                若是做多平倉則為-1，做空平倉為1
    '''
    _check_params(params, ['sign', 'ma1', 'ma2'])
    params = _convert_type(params, ['sign', 'ma1', 'ma2'], int)
    indicatorID = _valid_id(indicatorID)
    if indicatorID not in data_table.use_id['indicator']:
        raise RequirementNotMeetException('indicator ID %s not in Data Table\n' % indicatorID)
    if not (isinstance(params['ma1'], int) and isinstance(params['ma2'], int)):
        raise RequirementNotMeetException('ma1 and ma2 should be int\n')

    use_col = []
    indicatorDF = data_table.indicator[[indicatorID]].copy(deep=True)
    for ma in [params['ma1'], params['ma2']]:
        indicatorDF['ma-' + str(ma)] =\
            indicatorDF[indicatorID].rolling(ma).mean()
        use_col.append('ma-' + str(ma))
    
    indicatorDF['sign'] = 0
    if params['sign'] == 1:
        indicatorDF['sign'].loc[
            (indicatorDF[use_col[0]] > indicatorDF[use_col[1]])
        ] = 1
    elif params['sign'] == -1:
        indicatorDF['sign'].loc[
            (indicatorDF[use_col[0]] < indicatorDF[use_col[1]])
        ] = 1
    else:
        raise RequirementNotMeetException('sign should be either 1 or -1\n')

    indicatorDF['sign'] = indicatorDF['sign'].diff()
    dateList = indicatorDF['sign'].loc[
        (indicatorDF['sign'] == 1)
    ].index.values

    return dateList


def ma_crossover_price(data_table, indicatorID, params):
    '''
    params (dict):
        {
            'sign': 1,
            'ma': 20 
        }
    
    ma (int): 20
    sign (int): set([1, -1]) 做多為1，做空為-1
                若是做多平倉則為-1，做空平倉為1
    '''
    _check_params(params, ['sign', 'ma'])
    params = _convert_type(params, ['sign', 'ma'], int)
    indicatorID = _valid_id(indicatorID)
    if indicatorID not in data_table.use_id['indicator']:
        raise RequirementNotMeetException('indicator ID %s not in Data Table\n' % indicatorID)
    if not isinstance(params['ma'], int):
        raise RequirementNotMeetException('ma should be int\n')

    use_col = [str(indicatorID)]
    indicatorDF = data_table.indicator[[indicatorID]].copy(deep=True)
    for ma in [params['ma']]:
        indicatorDF['ma-' + str(ma)] =\
            indicatorDF[indicatorID].rolling(ma).mean()
        use_col.append('ma-' + str(ma))
    
    indicatorDF['sign'] = 0
    if params['sign'] == 1:
        indicatorDF['sign'].loc[
            (indicatorDF[use_col[0]] > indicatorDF[use_col[1]])
        ] = 1
    elif params['sign'] == -1:
        indicatorDF['sign'].loc[
            (indicatorDF[use_col[0]] < indicatorDF[use_col[1]])
        ] = 1
    else:
        raise RequirementNotMeetException('sign should be either 1 or -1\n')

    indicatorDF['sign'] = indicatorDF['sign'].diff()
    dateList = indicatorDF['sign'].loc[
        (indicatorDF['sign'] == 1)
    ].index.values

    return dateList