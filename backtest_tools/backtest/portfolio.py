import bt
from bt.backtest import Backtest, Result
from .composite import composite
from .performance import PerformanceMixin
from backtest_tools.helper import _check_params
from backtest_tools.data import getDataTable


class BacktestResult(Result, PerformanceMixin):
    pass


def RunBacktest(*backtests):
    '''
    adjusted bt.run
    '''
    for bkt in backtests:
        bkt.run()
    return BacktestResult(*backtests)


def runPortfolio(params):
    _check_params(
        params=params,
        list_to_check=['data_table', 'strategy']
    )

    data_table, comp = composite({
        'data_table': params['data_table'],
        'strategy': params['strategy']
    })

    start_date, end_date = data_table.date[0], data_table.date[-1]
    commission = None
    if params.get('start_date'):
        start_date = params['start_date']
    if params.get('end_date'):
        end_date = params['end_date']
    if params.get('commissions'):
        commission = params['commissions']

    trade = Backtest(**{
        'strategy': comp,
        'data': data_table.asset.loc[
            (data_table.asset.index >= start_date) &
            (data_table.asset.index <= end_date)
        ],
        'initial_capital': 1000000.0,
        'commissions': commission,
        'progress_bar': False
    })
    result = RunBacktest(trade)
    if params.get('riskfree_rate'):
        result.set_riskfree_rate(params['riskfree_rate'])

    return {
        'result': result,
        'strategy': trade
    }


def runComposite(params):
    _check_params(
        params=params,
        list_to_check=['data_table', 'strategy_list', 'strategy']
    )

    start_date = params['data_table'].date[0]
    end_date = params['data_table'].date[-1]
    commission = None
    if params.get('start_date'):
        start_date = params['start_date']
    if params.get('end_date'):
        end_date = params['end_date']
    if params.get('commissions'):
        commission = params['commissions']

    comp = RunBacktest(*params['strategy_list'])
    data_table = getDataTable({
        "asset": [
            {"name": v.prices.columns[0], "df": v.prices, "freq": "D"}
            for v in comp.values()
        ]
    })
    data_table, comp = composite({
        'data_table': data_table,
        'strategy': params['strategy']
    })

    trade = Backtest(**{
        'strategy': comp,
        'data': data_table.asset.loc[
            (data_table.asset.index >= start_date) &
            (data_table.asset.index <= end_date)
        ],
        'initial_capital': 1000000.0,
        'commissions': commission,
        'progress_bar': False
    })
    result = RunBacktest(trade)
    if params.get('riskfree_rate'):
        result.set_riskfree_rate(params['riskfree_rate'])

    return {
        'result': result,
        'strategy': trade
    }