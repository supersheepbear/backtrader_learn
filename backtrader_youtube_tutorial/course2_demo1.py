"""
Use pandas datafeed to read data
"""
# -*- coding:utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')


class MyStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def __init__(self):
        print('init')

    def start(self):
        print('start')

    def prenext(self):
        print("prenext")

    def nextstart(self):
        print("nextstart")

    def next(self):
        # print("next")
        ma_value = sum([self.data.close[-cnt] for cnt in range(0, 24)]) / 24
        ma_value_yesterday = sum([self.data.close[-cnt] for cnt in range(1, 25)]) / 25
        if self.data.close[0] > ma_value and self.data.close[-1] < ma_value_yesterday:
            self.order = self.buy()
        if self.data.close[0] < ma_value and self.data.close[-1] > ma_value_yesterday:
            self.order = self.sell()

    def stop(self):
        print("stop")


# 1. Create a cerebro
cerebro = bt.Cerebro(stdstats=False)
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
