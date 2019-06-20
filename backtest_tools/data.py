import pandas as pd
from .helper import _check_params


class DataTable(object):
    def __init__(self):
        self.use_id = {}
        self.frequency = None
        self.asset = pd.DataFrame()
        self.indicator = pd.DataFrame()
        self.date = pd.Series()

    def set_frequency(self):
        '''
        select the largest frequency
        '''
        freq_map = {
            'D': 0, 'W': 1, 'M': 2, 'Q': 3, 'H': 4, 'Y': 5,
        }
        freq_to_pandas = {
            'D': 'D', 'W': 'W-Mon', 'M': 'MS', 'Q': 'QS', 'H': 'YS', 'Y': 'YS',
        }

        set_freq = 0
        if isinstance(self.frequency, list):
            for f in self.frequency:
                set_freq = max(freq_map[f], set_freq)
            self.frequency = freq_to_pandas[
                [
                    k for k, v in freq_map.items() if v == set_freq
                ].pop()
            ]
        return True

    def check_validation(self):
        '''
        * check asset and indicator have the same frequency
        * check date is pandas datetime object
        * check asset and indicator have same date
        * check asset and indicator have no NaN
        * check asset and indicator's columns are all string
        '''
        self.asset.index = pd.DatetimeIndex(self.asset.index)
        self.asset.columns = [str(col) for col in self.asset.columns]

        if isinstance(self.frequency, str):
            self.asset = self.asset.apply(pd.to_numeric)
            self.asset = self.asset.resample(self.frequency).last()
            self.asset = self.asset.dropna()
            self.date = self.asset.index
            
        if not self.indicator.empty:
            self.indicator.index = pd.DatetimeIndex(self.indicator.index)
            self.indicator.columns = [
                str(col) for col in self.indicator.columns
            ]

            if isinstance(self.frequency, str):
                self.indicator = self.indicator.apply(pd.to_numeric)
                self.indicator = self.indicator.resample(self.frequency).last()
                self.indicator = self.indicator.dropna()

            self.date = sorted(
                list(set(self.asset.index).intersection(self.indicator.index))
            )
            self.indicator = self.indicator.loc[
                self.indicator.index.isin(self.date)
            ].replace({0: 0.000001}).sort_index()
        
        self.asset = self.asset.loc[
            self.asset.index.isin(self.date)
        ].sort_index()
        return True


def getDataTable(params):
    '''
    args:
        asset (list of dict): backtesting asset
        indicator (optional, list of dict): for trading condition
    example:
        params = {
            'asset': [{'name': 2, 'df': df, 'freq': 'M'}, ...],
            'indicator': [{'name': 2, 'df': df, 'freq': 'M'}, ...]
        }
    return DataTable object
    '''

    _check_params(
        params=params, 
        list_to_check=['asset']
    )

    data_table = DataTable()
    asset, indicator, freq = [], [], []
    ass_name, ind_name = [], []

    assetList = params['asset']
    if isinstance(assetList, dict):
        assetList = [params['asset']]

    for asset_dict in assetList:
        _check_params(
            params=asset_dict, 
            list_to_check=['name', 'df', 'freq']
        )
        asset.append(asset_dict['df'])
        freq.append(asset_dict['freq'])
        ass_name.append(str(asset_dict['name']))
    asset = pd.concat(asset, axis=1)
    asset.columns = ass_name

    if params.get('indicator'):
        if isinstance(params['indicator'], list):
            indicatorList = params['indicator']
        else:
            indicatorList = [params['indicator']]

        for ind_dict in indicatorList:
            _check_params(
                params=ind_dict, 
                list_to_check=['name', 'df', 'freq']
            )
            indicator.append(ind_dict['df'])
            freq.append(ind_dict['freq'])
            ind_name.append(str(ind_dict['name']))
        data_table.indicator = pd.concat(indicator, axis=1)
        data_table.indicator.columns = ind_name
    else:
        ind_name = None

    data_table.use_id = {
        'asset': ass_name, 
        'indicator': ind_name
    }
    data_table.frequency = freq
    data_table.asset = asset
    data_table.date = asset.index

    data_table.set_frequency()
    data_table.check_validation()
    return data_table