import json
import pickle
# from tools.ChartStat import ChartStat
from .portfolio import runPortfolio
from .exceptions import RequirementNotMeetException


class BacktestInterface(object):

    def __init__(self, asset, frequency='daily', commissions=None, start_date=None, end_date=None, **kwargs):
        self.params = dict.fromkeys(['data_table', 'strategy'], {})
        self.params['start_date'] = start_date
        self.params['end_date'] = end_date
        self.params['commissions'] = commissions


        if frequency not in ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']:
            RequirementNotMeetException('wrong input of backtesting frequency')
        self.params['strategy'] = [
            {'class': 'run_' + frequency, 'params': {}},
            {'class': 'select_all', 'params': {}},
            {'class': 'weigh_target', 'params': {'action': []}},
            {'class': 'rebalance', 'params': {}}
        ]


        if not (isinstance(asset, (int, str)) or isinstance(asset, list)):
            RequirementNotMeetException('wrong type for backtesting assets')
        if isinstance(asset, (int, str)):
            asset = [int(asset)]
        self.asset = asset
        self.indicator = [{'id': a} for a in asset]


    def addAction(self, action, ind_id, action_type, params, asset_id=None):
        if asset_id is None and len(self.asset) == 1:
            asset_id = self.asset[0]
        if int(ind_id) not in [ind['id'] for ind in self.indicator]:
            self.indicator.append({'id': int(ind_id)})

        sortOutParams = getattr(self, '{}_params'.format(action_type), None)
        if sortOutParams is not None:
            params = sortOutParams(params)

        self.params['strategy'][2]['params']['action'].append(
            {
                'asset_id': asset_id,
                'indicator_id': ind_id,
                'method': action_type,
                'strategy': action,
                'params': params
            }
        )


    # {}_params
    def ma_crossover_ma_params(self, params):
            params['ma1'] = params['ma_1']
            params['ma2'] = params['ma_2']
            del params['ma_1']
            del params['ma_2']
            return params


    def deleteAction(self, index):
        '''
        once delete a strategy the index of each strategy may change
        x = [1,2,3,4]
        del x[1]
        print(x) -> [1,3,4]
        '''
        del self.params['strategy'][2]['params']['action'][index]


    def replaceAction(self, index, action, ind_id, action_type, params, asset_id=None):
        '''
        replace the strategy at given index, the index order will not change
        x = [1,2,3,4]
        replace x[3] = 1
        print(x) -> [1,2,3,1]
        '''
        if asset_id is None and len(self.asset) == 1:
            asset_id = self.asset[0]
        
        self.params['strategy'][2]['params']['action'][index] = {
            'asset_id': asset_id,
            'indicator_id': ind_id,
            'method': action_type,
            'strategy': action,
            'params': params
        }
        

    def getParams(self, output='dict'):
        if output == 'pickle':
            return pickle.dumps(self.params, protocol=pickle.HIGHEST_PROTOCOL)
        elif output == 'json':
            return json.dumps(self.params)
        elif output == 'dict':
            return self.params
        return self.params


    def train(self):
        assetList, indList = [], []
        for stat_param in self.indicator:
            # TODO: implement data source 
            # tmp = ChartStat.formatter(stat_param, [], outputPandas=True)
            tmp_params = {
                'name': tmp['id'], 'freq': tmp['info']['frequency'], 
                'id': tmp['id'],
                'df': tmp['data'], 
            } 
            if stat_param['id'] in self.asset:
                assetList.append(tmp_params)
            indList.append(tmp_params)

        if len(assetList)==0 or len(indList)==0:
            RequirementNotMeetException('should provide at least one asset')
        
        self.params['data_table']['asset'] = assetList
        self.params['data_table']['indicator'] = indList

        result = runPortfolio(self.params)
        return result


    def save(res, path):
        with open(path, 'wb') as f:
            pickle.dump(res, f, protocol=pickle.HIGHEST_PROTOCOL)

    
    def load(path): 
        with open(path, 'rb') as f:
            res = pickle.load(f)
        return res

