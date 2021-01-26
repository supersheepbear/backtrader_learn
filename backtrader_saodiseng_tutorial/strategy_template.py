"""
A self made indicator example
"""
# -*- coding:utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader as bt
import pandas as pd
# from backtrader_plotting import Bokeh
# from backtrader_plotting.schemes import Tradimo
# import quantstats as qs
import os


class XXIndicator(bt.Indicator):
    params = ('xx',)
    lines = ('xx', 'yy')

    def __init__(self):
        # Add minimum period
        self.addminperiod(4)
        # plot master means plot on the main subplot
        # if not having this line, indicator will be plotted in another subplot
        self.plotinfo.plotmaster = self.data

    def next(self):
        pass


class MyStrategy(bt.Strategy):
    params = (
        ('xx', 24),
    )

    def __init__(self):
        pass

    def start(self):
        pass

    def prenext(self):
        pass

    def nextstart(self):
        pass

    def next(self):
        pass

    def stop(self):
        pass


if __name__ == '__main__':
    # Create a cerebro
    cerebro = bt.Cerebro()
    # Add data feed

    dataframe = pd.read_csv(r'MES.csv')
    dataframe.columns = ['date',
                         'open',
                         'high',
                         'low',
                         'close',
                         'volume',
                         'openinterest']

    dataframe['date'] = pd.to_datetime(dataframe['date'], format='%Y-%m-%d')
    dataframe = dataframe.sort_values("date")
    dataframe.set_index('date', inplace=True)

    data = bt.feeds.PandasData(dataname=dataframe)

    cerebro.adddata(data)

    # Add strategy
    cerebro.addstrategy(MyStrategy)

    # set broker
    cerebro.broker.setcash(20000.0)

    # set commission
    cerebro.broker.setcommission(commission=0.0003, commtype=bt.comminfo.CommInfoBase.COMM_PERC, margin=0)

    # set slippage
    cerebro.broker.set_slippage_perc(perc=0.0005)

    # Add observers
    # cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell)
    # cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.Value)
    cerebro.addobserver(bt.observers.TimeReturn)

    # Add analyser
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')  # 加入PyFolio分析者
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    # cerebro.addanalyzer(bt.analyzers.Transactions)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Add writer
    # cerebro.addwriter(bt.WriterFile, csv=True, out=os.path.basename(__file__) + '.csv')

    # Run over everything
    results = cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot result
    cerebro.plot(style='candle', iplot=False)

    # Add writer
    # cerebro.addwriter(bt.WriterFile, csv=True, out=__name__ + '.csv')

    # quantstats output
    """
    strat = results[0] # 获得策略实例

    portfolio_stats = strat.analyzers.getbyname('PyFolio') # 得到PyFolio分析者实例
    # 以下returns为以日期为索引的资产日收益率系列
    returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()

    returns.index = returns.index.tz_convert(None) # 索引的时区要设置一下，否则出错

    # 输出html策略报告,rf为无风险利率
    qs.reports.html(returns, output='stats.html', title='策略绩效报告', rf=0.0)

    print(qs.reports.metrics(returns=returns, mode='basic'))

    df = qs.reports.metrics(returns=returns, mode='basic', display=False)

    qs.reports.basic(returns)
    """

    # backtrader_plotting
    """
     b = Bokeh(style='bar') # 黑底, 单页
     b = Bokeh(style='bar', tabs='multi') # 黑底, 多页
     b = Bokeh(style='bar', scheme=Tradimo()) # 传统白底, 单页
     b = Bokeh(style='bar', tabs='multi', scheme=Tradimo()) # 传统白底, 多页
     cerebro.plot(b)
    """

    # print out result
    """
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Print drawdown result
    # The default name of analyzers is the lower case of the class name
    print("DrawDown: ")
    # Use pretty print to print the original returned dictionary
    #pprint.pprint(res.analyzers.drawdown.get_analysis())
    # print only interested values
    drawdown_data = res.analyzers.drawdown.get_analysis()
    print('max drawdown: %s %%' % drawdown_data['max']['drawdown'])
    print('max money drawdown: %s' % drawdown_data['max']['moneydown'])

    # Print trade analyzer result
    print("Trade result")
    # Use pretty print to print the original returned dictionary
    #pprint.pprint(res.analyzers.tradeanalyzer.get_analysis())
    trading_data = res.analyzers.tradeanalyzer.get_analysis()
    print("===won===")
    print("won_ratio: %s" % str(trading_data['won']['total'] / float(trading_data['won']['total'] + trading_data['lost']['total'])))
    print("won_hits: %s" % trading_data['won']['total'])
    print("won_pnl-->total:%s, average:%s, max:%s" %
          (
              trading_data['won']['pnl']['total'],
              trading_data['won']['pnl']['average'],
              trading_data['won']['pnl']['max']
          )
          )

    print("===lost===")
    print("lost_hits: %s" % trading_data['lost']['total'])
    print("lost_pnl-->total:%s, average:%s, max:%s" %
          (
              trading_data['lost']['pnl']['total'],
              trading_data['lost']['pnl']['average'],
              trading_data['lost']['pnl']['max']
          )
          )

    print("===long position===")
    print("long_hits: %s" % trading_data['long']['total'])
    print("long_pnl-->total:%s, average:%s" %
          (
              trading_data['long']['pnl']['total'],
              trading_data['long']['pnl']['average']
          )
          )

    print("===short position===")
    print("short_hits: %s" % trading_data['short']['total'])
    print("short_pnl-->total:%s, average:%s" %
          (
              trading_data['short']['pnl']['total'],
              trading_data['short']['pnl']['average']
          )
          )
    """