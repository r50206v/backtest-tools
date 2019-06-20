from bt.core import Strategy
from bt.algos import run_always
import uuid
import importlib
from .strategy import *
from backtest_tools.helper import _check_params
from backtest_tools.data import getDataTable


def composite(params):
    '''
    construct strategy composite for portfolio
    using bt.core.Strategy
    Args: 
        params (dict): containing keys `data`, `strategy` 
            data_table (dict): follow the rules of data.py
            strategy (list): list of dictionary, containing all params that each strategy needs

    --------------------------------------------------
    Strategy(class):
        Args:
        * name (str): Strategy name
        * algos (list): List of Algos to be passed into an AlgoStack
        * children (dict, list): Children - useful when you want to create
            strategies of strategies

        Attributes:
        * stack (AlgoStack): The stack
        * temp (dict): A dict containing temporary data - cleared on each call
            to run. This can be used to pass info to other algos.
        * perm (dict): Permanent data used to pass info from one algo to
            another. Not cleared on each pass.
    '''
    _check_params(params, ['data_table', 'strategy'])

    name = uuid.uuid4()
    data_table = getDataTable(params['data_table'])
    
    StrategyList = []
    for stra in params['strategy']:
        pkg = importlib.import_module('backtest_tools.backtest.strategy')
        func = getattr(pkg, stra['class'])
        func = run_always(func)

        inputs = {}
        inputs['data_table'] = data_table
        inputs['params'] = {}
        if stra.get('params'):
            inputs['params'] = stra['params']
        
        StrategyList.append(func(**inputs))
    
    s = Strategy(**{
        'name': name,
        'algos': StrategyList,
        'children': None
    })
    return data_table, s