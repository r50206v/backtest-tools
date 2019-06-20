from bt.algos import *
from .customized_strategy import *
from backtest_tools.helper import _check_params


def run_once(data_table, params):
    return RunOnce(**params)


def run_daily(data_table, params):
    '''
    default params
    run_on_first_date=True, run_on_end_of_period=False, run_on_last_date=False
    '''
    return RunDaily(**params)


def run_weekly(data_table, params):
    '''
    default params
    run_on_first_date=True, run_on_end_of_period=False, run_on_last_date=False
    '''
    return RunWeekly(**params)


def run_monthly(data_table, params):
    '''
    default params
    run_on_first_date=True, run_on_end_of_period=False, run_on_last_date=False
    '''
    return RunMonthly(**params)


def run_quarterly(data_table, params):
    '''
    default params
    run_on_first_date=True, run_on_end_of_period=False, run_on_last_date=False
    '''
    return RunQuarterly(**params)


def run_yearly(data_table, params):
    '''
    default params
    run_on_first_date=True, run_on_end_of_period=False, run_on_last_date=False
    '''
    return RunYearly(**params)


def run_on_date(data_table, params):
    '''
    ** NO default params
    dates: List of dates to run Algo on. 
        - format: ['yyyy-mm-dd', 'yyyy-mm-dd', 'yyyy-mm-dd'...]
    '''
    _check_params(params, ['dates'])
    return RunOnDate(**params)


def run_after_date(data_table, params):
    '''
    ** NO default params
    date (string): a specific date.
        - format: 'yyyy-mm-dd'
    '''
    _check_params(params, ['date'])
    return RunAfterDate(**params)


def run_after_days(data_table, params):
    '''
    ** NO default params
    days (int): Number of trading days to wait before starting 
    '''
    _check_params(params, ['days'])
    return RunAfterDays(**params)


def run_every_n_periods(data_table, params):
    '''
    ** NO default params
    n (int): Run each n periods
    offset (int): Applies to the first run. If 0, this algo will run the
        first time it is called.
    '''
    _check_params(params, ['n', 'offset'])
    return RunEveryNPeriods(**params)


def select_all(data_table, params):
    '''
    default params
    include_no_data=False
    '''
    return SelectAll(**params)


def select_these(data_table, params):
    '''
    default params
    include_no_data=False

    ** NO default params
    tickers (list): List of tickers to select.
    '''
    _check_params(params, ['tickers'])
    return SelectThese(**params)


def select_has_data(data_table, params):
    '''
    default params
    lookback=pd.DateOffset(months=3),
    min_count=None, 
    include_no_data=False

    Args:
        * lookback (DateOffset): A DateOffset that determines the lookback
            period.
        * min_count (int): Minimum number of days required for a series to be
            considered valid. If not provided, ffn's get_num_days_required is
            used to estimate the number of points required.
    '''
    return SelectHasData(**params)


def select_n(data_table, params):
    '''
    ** NO default params
    n (int): select top n items.

    default params
    sort_descending=True,
    all_or_none=False
    '''
    _check_params(params, ['n'])
    return SelectN(**params)


def stat_total_return(data_table, params):
    '''
    default params
    lookback=pd.DateOffset(months=3),
    lag=pd.DateOffset(days=0)
    '''
    return StatTotalReturn(**params)


def select_momentum(data_table, params):
    '''
    ** NO default params
    n (int): select first N elements

    Args:
        * n (int): select first N elements
        * lookback (DateOffset): lookback period for total return
            calculation
        * lag (DateOffset): Lag interval for total return calculation
        * sort_descending (bool): Sort descending (highest return is best)
        * all_or_none (bool): If true, only populates temp['selected'] if we
            have n items. If we have less than n, then temp['selected'] = [].
    '''
    _check_params(params, ['n'])
    return SelectMomentum(**params)


def weigh_equally(data_table, params):
    return WeighEqually(**params)


def weigh_specificed(data_table, params):
    '''
    ** NO default params
    weights (dict): target weights -> ticker: weight
    '''
    _check_params(params, ['weights'])
    return WeighSpecified(**params)


def weigh_inverse_volatility(data_table, params):
    '''
    default params
    lookback=pd.DateOffset(months=3),
    lag=pd.DateOffset(days=0)
    '''
    return WeighInvVol(**params)


def weigh_erc(data_table, params):
    '''
    default params
    lookback=pd.DateOffset(months=3),
    initial_weights=None,
    risk_weights=None,
    covar_method='ledoit-wolf',
    risk_parity_method='ccd',
    maximum_iterations=100,
    tolerance=1E-8,
    lag=pd.DateOffset(days=0)
    '''
    return WeighERC(**params)


def weigh_mean_variance(data_table, params):
    '''
    default params
    lookback=pd.DateOffset(months=3),
    bounds=(0., 1.), 
    covar_method='ledoit-wolf',
    rf=0., 
    lag=pd.DateOffset(days=0)
    '''
    return WeighMeanVar(**params)


def weigh_randomly(data_table, params):
    '''
    default params
    bounds=(0., 1.), 
    weight_sum=1
    '''
    return WeighRandomly(**params)


def limit_deltas(data_table, params):
    '''
    default params
    limit=0.1
    '''
    return LimitDeltas(**params)


def limit_weights(data_table, params):
    '''
    default params
    limit=0.1
    '''
    return LimitWeights(**params)


def target_volatility(data_table, params):
    '''
    ** NO default params
    target_volatility,

    default params
    lookback=pd.DateOffset(months=3),
    lag=pd.DateOffset(days=0),
    covar_method='standard',
    annualization_factor=252
    '''
    _check_params(params, ['target_volatility'])
    return TargetVol(**params)


def pte_rebalance(data_table, params):
    '''
    ** NO default params
    PTE_volatility_cap,
    target_weights,

    default params
    lookback=pd.DateOffset(months=3),
    lag=pd.DateOffset(days=0),
    covar_method='standard',
    annualization_factor=252
    '''
    _check_params(params, ['PTE_volatility_cap', 'target_weights'])
    return PTE_Rebalance(**params)


def capital_flow(data_table, params):
    '''
    ** NO default params 
    amount (float): Amount of adjustment
    '''
    _check_params(params, ['amount'])
    return CapitalFlow(**params)


def close_dead(data_table, params):
    return CloseDead(**params)


def rebalance(data_table, params):
    return Rebalance(**params)


def rebalance_over_time(data_table, params):
    '''
    default params
    n = 10 (number of periods over which rebalancing takes place.)
    '''
    return RebalanceOverTime(**params)
