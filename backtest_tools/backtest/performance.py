import operator
import numpy as np
import pandas as pd
import scipy.stats as ss
from itertools import product


class PerformanceMixin(object):
    ''' 
    Mixin for calculating strategy criteria

    TODO: 近期表現, 策略屬性

    kelly , 獲利風險比, 
    VaR, `VoL`, 勝率, 
    累積交易次數, `交易成本`, 
    平均交易盈虧, 平均交易中位數, 
    最大回檔幅度, `報酬率`, 
    payoff ratio, profit factor
    reference: https://www.amibroker.com/guide/h_report.html
    '''

    def trading_times(self):
        return len(self.get_transactions()['quantity'])

    def returns(self, strategy_name=None):
        # extract strategy given strategy_name
        if strategy_name is None:
            strategy_name = self.backtest_list[0].name
        s = self.backtests[strategy_name].strategy

        positions = pd.DataFrame({x.name: x.positions for x in s.securities})
        prices = pd.DataFrame({x.name: x.prices for x in s.securities})

        # calculate each trade and adjust first row
        trades = positions.diff()
        trades.iloc[0] = positions.iloc[0]


        def _between_date(start, end, all_dates):
            '''modified pandas.DatetimeIndex.indexer_between_time'''
            lop = operator.lt
            if start is None:
                lop = operator.le
                start = all_dates[0]
            mask = operator.and_(
                lop(start, all_dates),
                operator.le(all_dates, end)
            )
            return mask.nonzero()[0]
        
        
        # calculate returns
        returnsList = []
        last_date = None
        for col in trades.columns:
            trading = trades[col]
            trading = trading[trading != 0].dropna()
            # get trading dates and the price
            trading_dates = np.append(trading.index.tolist(), prices.index[-1])

            data = pd.concat([trading, prices[col]], axis=1).loc[trading_dates]
            data.columns = ['trade', 'price']
            # find out when the portfolio takes profit (找到獲利了結的時間點)
            for time in data.loc[data['trade'].cumsum() == 0].index:
                tmp = data.iloc[ _between_date(last_date, time, trading.index) ]
                tmp['value'] = tmp['trade'].abs() * tmp['price']
                value = tmp['value'].iloc[-1] - tmp['value'].iloc[:-1].sum()
                returnsList.append(value)

                last_date = time
            last_date = None
        self.returnsList = np.array(returnsList)

    def win_rate(self):
        '''
        def: %Wins = Number of wins divided by total number of trades 
        '''
        returns = self.returnsList
        win_rate = sum(returns > 0) / len(returns)
        return win_rate

    def profit_factor(self):
        '''
        def: Profit of winners divided by loss of losers
        '''
        returns = self.returnsList
        return returns[returns > 0].sum() / np.abs(returns[returns < 0].sum())

    def payoff_ratio(self):
        '''
        def: avg win / avg loss
        '''
        returns = self.returnsList
        return returns[returns > 0].mean() / np.abs(returns[returns < 0].mean())

    def profit_dropdown(self, strategy_name=None):
        '''
        def: net profit / max dropdown value
        '''
        # extract strategy given strategy_name
        if strategy_name is None:
            strategy_name = self.backtest_list[0].name
        strat_info = self.backtests[strategy_name]

        def _drawdown(prices):
            # modify from ffn/core.py def to_drawdown_series
            p = prices.copy(deep=True)
            p = p.fillna(method='ffill')
            p[np.isnan(p)] = -np.Inf
            return p - np.maximum.accumulate(p)

        dropdown = abs(min( _drawdown(strat_info.strategy.prices) ))
        net_profit = strat_info.strategy.prices.iloc[-1] - 100 # 期末權益-期初權益
        return net_profit / dropdown

    def value_at_risk(self, alpha=0.05, strategy_name=None):
        '''
        def: estimate normal distribution for daily returns
            and return the lower bound of confidence interval in alpha
        '''
        # extract strategy given strategy_name
        if strategy_name is None:
            strategy_name = self.backtest_list[0].name
        s = self.backtests[strategy_name].strategy

        daily_returns = s.prices.to_returns().dropna()
        var = ss.norm.ppf(alpha, daily_returns.mean(), daily_returns.std())
        return var

    def kelly(self):
        '''
        def: win_rate - (1-win_rate)/payoff_ratio
        '''
        p = self.win_rate()
        q = 1 - p
        b = self.payoff_ratio()
        return p - (q/b)

    def sharp_ratio(self, strategy_name=None):
        if strategy_name is None:
            strategy_name = self.backtest_list[0].name
        stats = self.backtests[strategy_name].stats.stats
        if not pd.isnull(stats.loc['daily_sharpe']):
            return stats.loc['daily_sharpe']
        elif not pd.isnull(stats.loc['monthly_sharpe']):
            return stats.loc['monthly_sharpe']
        elif not pd.isnull(stats.loc['yearly_sharpe']):
            return stats.loc['yearly_sharpe']

    def getReport(self, strategy_name=None):
        try:
            self.returns()
        except IndexError as e:
            if str(e) == 'single positional indexer is out-of-bounds':
                e = "warnings: no any indicators meet the conditions"
            result = dict.fromkeys(['profit_dropdown','kelly','sharp_ratio','ROI','annual_ROI','annual_VOL','value_at_risk','equity','dropdown','weights','trade_returns','win_rate','trading_times','profit_factor','payoff_ratio'], 0)
            result['message'] = str(e)
            return result

        if strategy_name is None:
            strategy_name = self.backtest_list[0].name
        strat_info = self.backtests[strategy_name]
        
        equity = strat_info.strategy.prices
        equity.index = equity.index.strftime('%Y-%m-%d')
        dropdown = strat_info.stats.drawdown
        dropdown.index = dropdown.index.strftime('%Y-%m-%d')
        weights = strat_info.security_weights
        weights.index = weights.index.strftime('%Y-%m-%d')

        def _NullToDash(x):
            if pd.isnull(x):
                return '-'
            else:
                return x

        return {
            'profit_dropdown': self.profit_dropdown(),
            'kelly': self.kelly(),
            'sharp_ratio': self.sharp_ratio(),
            'return_of_investment': _NullToDash(strat_info.stats.stats.loc['total_return']),
            'annualized_returns': _NullToDash(strat_info.stats.stats.loc['cagr']),
            'yearly_volatility': _NullToDash(strat_info.stats.stats.loc['yearly_vol']),
            'value_at_risk': self.value_at_risk(),
            'equity': equity.reset_index().values.tolist(),
            'dropdown': dropdown.reset_index().values.tolist(),
            'weights': weights.reset_index().values.tolist(),
            'trade_returns': self.returnsList.tolist(),
            'win_rate': self.win_rate(),
            'trading_times': self.trading_times(),
            'profit_factor': self.profit_factor(),
            'payoff_ratio': self.payoff_ratio(),
            'message': 'succeed',
            'max_dropdown': _NullToDash(strat_info.stats.max_drawdown)
        }