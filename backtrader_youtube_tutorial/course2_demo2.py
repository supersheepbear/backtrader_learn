"""
sma strategy with sma indicator
"""
# -*- coding:utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader as bt
import pandas as pd


class MyStrategy(bt.Strategy):
    params = (
        ('maperiod', 24),
    )

    def __init__(self):
        self.bt_sma = bt.indicators.MovingAverageSimple(self.data, period=24)
        self.buy_sell_signal = bt.indicators.CrossOver(self.data.close, self.bt_sma)

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
        if not self.position and self.buy_sell_signal[0] == 1:
            self.order = self.buy()

        if not self.position and self.buy_sell_signal[0] == -1:
            self.order = self.sell()

        if self.position and self.buy_sell_signal[0] == 1:
            self.order = self.close()
            self.order = self.buy()

        if self.position and self.buy_sell_signal[0] == -1:
            self.order = self.close()
            self.order = self.sell()

    def stop(self):
        print("stop")


# 1. Create a cerebro
cerebro = bt.Cerebro()
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

# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Run over everything
cerebro.run()

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 5. Plot result
cerebro.plot(style='candle')
