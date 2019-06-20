# MMtools
*last change in 2018-12-07*

provides `backtest` and `correlation` two sub-modules
\
main packages: pandas, numpy, scipy, bt, ffn

### structure: 
![](https://i.imgur.com/uUOKQvh.png)

#### 1. `requirements.txt`
containing all required packages(**not** indicating specific package version)
\
how to use: `pip install -r PATH/MMtools/requirements.txt`

#### 2. `helper.py`
containing all helper function, such as `_check_params`, `_valid_id`

#### 3. `data.py`
> interface: `def foo(dict: params)`

containing DataTable(class) and getDataTable(function) 

DataTable includes 2 functions (`check_validation`, `set_frequecny`) and 5 attributes (`dict: use_id`, `string: frequency`, `pd.DataFrame: asset`, `pd.DataFrame: indicator`, `pd.Series: date`)
```
**class DataTable:
use_id = {
    'asset': list of stat_id,
    'indicator': list of stat_id
}
frequency: one of [D, W-Mon, MS, QS, YS]
asset, indicator: 
    columns: pd.Index(list of str(stat_id))
    index: pd.DatetimeIndex
    values: int or float
date: pd.DatetimeIndex
``` 
```
**func getDataTable(dict: params)
params = {
    'asset': list of dictionary,
    'indicator'(optional): list of dictionary
}

example: 
params = {
    'asset': [{'name': 's&p500', 'df': pd.DataFrame, 'freq': 'D'}],
    'indicator': [{'name': '10y-2y', 'df': pd.DataFrame, 'freq': 'D'}]
},
```

<br><br>
# Backtesting

### package: bt(main), ffn
#### four main reasons to use bt:
1. **Tree Structure**
>The tree structure facilitates the construction and composition of complex algorithmic trading strategies that are modular and re-usable.
2. **Algorithm Stacks**
> Algos and AlgoStacks are another core feature that facilitate the creation of modular and re-usable strategy logic.
3. Charting and Reporting
4. Detailed Statistics

<br><br>
### Simple Example:
*more complex examples are provided below*
```
params = {
    'data_table': {
        'asset': [{'name': 's&p500', 'df': pd.DataFrame, 'freq': 'D'}],
        'indicator': [{'name': '10y-2y', 'df': pd.DataFrame, 'freq': 'D'}]
    },
    'strategy': [
        {'class': 'run_monthly', 'params': {}},
        {'class': 'select_all', 'params': {}},
        {'class': 'weigh_equally', 'params': {}},
        {'class': 'rebalance', 'params': {}}
    ],
    'start_date': '2011-01-01',
    'end_date': '2018-10-01',
    'commission': lambda q, p: max(1, abs(q)*0.01)
}

result = Portfolio(params)

# portfolio statistics
result['result'].display()

# equity-plot
result['result'].plot()

# store result
with open(path + 'sample-data/backtest-result.pkl', 'wb') as f:
    pickle.dump(result['result'], f, protocol=pickle.HIGHEST_PROTOCOL)
with open(path + 'sample-data/trade-info.pkl', 'wb') as f:
    pickle.dump(result['strategy'], f, protocol=pickle.HIGHEST_PROTOCOL)
```

<br><br>
### structure: 
![](https://i.imgur.com/3j9qJzN.png)

#### 1. `strategy.py` `customized_strategy.py`
> interface: `def foo(DataTable: data_table, dict: params)`

repacking bt.algos class into several functions, and each function follows the same interface(`data_table`, `params`), however, `params` changes according to features
```
def run_daily(data_table, params):
    '''
    params (dict)
    default: run_on_first_date=True
    '''
    return RunDaily(**params)
```

- user can add strategies in `customized_strategy.py` by packing `bt.algos.SelectWhere`, `bt.algos.WeighTarget` into functions, and should follow the interface rule
- we now provide `trade_at_threshold`, `continuous_growth`, `cumulative_return_threshold`, `specific_date` for users


#### 2. `composite.py`
> interface: `def foo(dict: params)`

stacking all algorithms into one strategy for execution
```
Args: 
params (dict): containing keys `data`, `strategy` 
    data_table (dict): follow the rules of data.py
    strategy (list): list of dictionary, containing all params that each strategy needs
    
Return:
(data_table, strategy)
```

#### 3. `performance.py`
Mixin for customized strategy criteria
we now provide 
`trading_times`, `returns`, `win_rate`, `profit_factor`, `payoff_ratio`, `profit_dropdown`, `value_at_risk`, `kelly`

result.getMMReport() returns this dictionary
```
{
    'profit_dropdown': 獲利因子比, 
    'kelly': kelly formula,
    'sharp_ratio': sharp ratio,
    'ROI': 報酬率,
    'annual_ROI': 年化報酬率,
    'annual_VOL': 年化波動率,
    'value_at_risk': 風險值,
    'equity': 權益dataframe,
    'dropdown': 回檔變化dataframe,
    'weights': 資產權重dataframe,
    'trade_returns': 交易盈虧List,
    'win_rate': 勝率,
    'trading_times': 交易次數,
    'profit_factor': profit factor,
    'payoff_ratio': payoff ratio
}
```

#### 4. `portfolio.py`
> interface: `def foo(dict: params)`

backtesting
```
Args:
params (dict): containing keys `data_table`, `strategy` 
    (optional keys) `start_date`, `end_date`, `commission` 
    data_table (dict): follow the rules of data.py
    strategy (list): follow the rules of composite.py
    - start_date: string in %Y-%m-%d format
    - end_date: string in %Y-%m-%d format
    - commission: lambda quantity, price: func(quantity, price)
```

### Examples:

#### Ex1
1. buy `2` when `337` yoy > 0
2. sell `2` when `337` yoy < 0
3. sell `32` when `268` remains smaller than 0 for 5 periods
4. buy `32` when `268` remains greater than 0 for 5 periods
```
params = {
    'data_table': {
        'asset': [{'name': 's&p500', 'df': pd.DataFrame, 'freq': 'D'}],
        'indicator': [{'name': '10y-2y', 'df': pd.DataFrame, 'freq': 'D'}]
    },
    'strategy': [
        {'class': 'run_monthly', 'params': {}},
        {'class': 'select_all', 'params': {}},
        {'class': 'weigh_target', 'params': {
            'action': [
                {
                    'indicator_id': 337,
                    'method': 'cumulative_return_threshold',
                    'asset_id': 2,
                    'strategy': 'buy',
                    'params': {
                        'n': 12, 'sign': 1, 'threshold': 0
                    }
                },
                {
                    'indicator_id': 337,
                    'method': 'cumulative_return_threshold',
                    'asset_id': 2,
                    'strategy': 'sell',
                    'params': {
                        'n': 12, 'sign': -1, 'threshold': 0
                    }
                },
                {
                    'indicator_id': 268,
                    'method': 'trade_at_threshold',
                    'asset_id': 32,
                    'strategy': 'sell',
                    'params': {
                        'n': 5, 'sign': -1, 'threshold': 0
                    }
                },
                {
                    'indicator_id': 268,
                    'method': 'trade_at_threshold',
                    'asset_id': 32,
                    'strategy': 'buy',
                    'params': {
                        'n': 5, 'sign': 1, 'threshold': 0
                    }
                }
            ]
        }},
        {'class': 'rebalance', 'params': {}}
    ],
    'start_date': '2000-01-01',
    'commissions': lambda q, p: max(1, p*0.015)
}


result = Portfolio(params)

# get kelly value
result['result'].kelly()

# get asset weights plot
result['result'].plot_security_weights()

# get dropdown plot
result['result'].prices.to_drawdown_series().plot()
```

#### Ex2
1. buy `2` when `2`'s 5-day moving average larger than 20-day moving average
2. sell `2` when `2`'s 5-day moving average smaller than 20-day moving average
3. sell `32` when `32`'s current price smaller than 120-day moving average
4. buy `32` when `32`'s current price larger than 120-day moving average
```
params = {
    'data_table': {
        'asset': [{'name': 's&p500', 'df': pd.DataFrame, 'freq': 'D'}],
        'indicator': [{'name': '10y-2y', 'df': pd.DataFrame, 'freq': 'D'}]
    },
    'strategy': [
        {'class': 'run_monthly', 'params': {}},
        {'class': 'select_all', 'params': {}},
        {'class': 'weigh_target', 'params': {
            'action': [
                {
                    'indicator_id': 2,
                    'method': 'ma_crossover',
                    'asset_id': 2,
                    'strategy': 'buy',
                    'params': {
                        'ma': [5, 20], 'sign': 1
                    }
                },
                {
                    'indicator_id': 2,
                    'method': 'ma_crossover',
                    'asset_id': 2,
                    'strategy': 'sell',
                    'params': {
                        'ma': [5, 20], 'sign': -1
                    }
                },
                {
                    'indicator_id': 32,
                    'method': 'ma_crossover',
                    'asset_id': 32,
                    'strategy': 'sell',
                    'params': {
                        'ma': [120], 'sign': -1
                    }
                },
                {
                    'indicator_id': 32,
                    'method': 'ma_crossover',
                    'asset_id': 32,
                    'strategy': 'buy',
                    'params': {
                        'ma': [120], 'sign': 1
                    }
                }
            ]
        }},
        {'class': 'rebalance', 'params': {}}
    ],
    'start_date': '2000-01-01',
    'commissions': lambda q, p: max(1, p*0.015)
}
```

<br><br>
# Correlation

### package: scipy(main)
### core concept: 
calculate the cross-correlation function for an asset with an indicator

### steps:
1. get DataTable (should only have one asset and one indicator)
2. Detrend: convert to stationary series (we know only provide boxcox transformation)
3. Cross-Correlation Function / R2 

### Examples:
```
params = {
    'data_table': {
        'asset': [{'name': 's&p500', 'df': pd.DataFrame, 'freq': 'D'}],
        'indicator': [{'name': '10y-2y', 'df': pd.DataFrame, 'freq': 'D'}]
    },
    'start_date': '2006-01-01',
    'stationary': 'boxcox',
    'correlation': 'ccf'
}
result = getCorrelation(params)
```
this will return `{'correlation': 0.51676792, 'period': 4, 'status': 'ahead'}`

### structure:
#### 1. ccf:
```
func getCorrelation(params: dict)

params:
{
    'data_table': params same as data.py
    'start_date': (optional) datetime format str,
    'end_date': (optional) datetime format str,
    'max_lags': (optional) 0 or positive int,
    'stationary': (optional) str,
    'correlation': (optional) str,
}

return:
{
    'correlation': 'r2',
    'value': float,
    'period': [positive int],
    'status': str,
    'stationary': [{col_name: str}, ...],
    'frequency': str,
    'date': [start_date, end_date],
    'significant': {str(int): {"significant": boolean, "coefficient": float}},
    'adf-test': {col_name: float}
}

{
    'correlation': 'ccf',
    'value': float,
    'period': [positive int],
    'status': str,
    'stationary': [{col_name: str}, ...],
    'frequency': str,
    'date': [start_date, end_date],
    'significant': {str(int): {"significant": boolean, "value": float}},
    'adf-test': {col_name: float}
}
```

###### tags: `macromicro` `backtest` `correlation`

