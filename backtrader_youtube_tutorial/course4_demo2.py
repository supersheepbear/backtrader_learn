"""
An example of setting writter
"""
# -*- coding:utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader as bt
import pandas as pd


class ThreeBars(bt.Indicator):
    params = (('size', 3),)
    lines = ('up', 'down')

    def __init__(self):
        # Add minimum period
        self.addminperiod(4)
        # plot master means plot on the main subplot
        # if not having this line, indicator will be plotted in another subplot
        self.plotinfo.plotmaster = self.data

    def next(self):
        # self.up[0] = max(max(self.data.close.get(ago=-1, size=3)), min(self.data.open.get(ago=-1, size=3)))
        self.lines[0][0] = max(max(self.data.close.get(ago=-1, size=self.p.size)),
                               min(self.data.open.get(ago=-1, size=self.p.size)))
        self.down[0] = min(min(self.data.close.get(ago=-1, size=self.p.size)),
                           min(self.data.open.get(ago=-1, size=self.p.size)))


class MyStrategy(bt.Strategy):
    params = (
        ('maperiod', 24),
    )

    def __init__(self):
        self.up_down = ThreeBars(self.data)
        self.buy_signal = bt.indicators.CrossOver(self.data.close, self.up_down.up)
        self.sell_signal = bt.indicators.CrossDown(self.data.close, self.up_down.down)
        # Turn off plot for buy and sell signals
        self.buy_signal.plotinfo.plot = False
        self.sell_signal.plotinfo.plot = False
        self.up_down.plotinfo.plot = False

    def start(self):
        print('start')

    def prenext(self):
        #print("prenext")
        pass

    def nextstart(self):
        print("nextstart")

    def next(self):
        #ma_value = self.bt_sma[0]
        #ma_value_yesterday = self.bt_sma[-1]
        if not self.position and self.buy_signal[0] == 1:
            self.order = self.buy()

        # self.getposition().size can return size of current portfolio
        if self.getposition().size < 0 and self.buy_signal[0] == 1:
            self.order = self.close()
            self.order = self.buy()

        if not self.position and self.sell_signal[0] == 1:
            self.order = self.sell()

        if self.getposition().size > 0 and self.sell_signal[0] == 1:
            self.order = self.close()
            self.order = self.sell()

    def stop(self):
        print("stop")


if __name__ == '__main__':
    # 1. Create a cerebro
    cerebro = bt.Cerebro()
    cerebro.addobserver(bt.observers.TimeReturn)
    # 2. Add data feed
    # 2.1  Create a data feed

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

    # 2.2 Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # 3. Add strategy
    cerebro.addstrategy(MyStrategy)

    # set broker
    cerebro.broker.setcash(20000.0)

    # set commission
    cerebro.broker.setcommission(commission=0.0003, commtype=bt.comminfo.CommInfoBase.COMM_PERC, margin=0)

    # set slippage
    cerebro.broker.set_slippage_perc(perc=0.0005)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Add some analyzers
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)

    # Add writer
    cerebro.addwriter(bt.WriterFile, csv=True, out='backtest_result.csv')

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 5. Plot result
    cerebro.plot(style='candle')
