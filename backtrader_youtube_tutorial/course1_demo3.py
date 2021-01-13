"""
Use pandas datafeed to read data
"""
# -*- coding:utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import backtrader as bt
import pandas as pd


class MyStrategy(bt.Strategy):

    def __init__(self):
        print('init')

    def start(self):
        print('start')

    def prenext(self):
        print("prenext")

    def nextstart(self):
        print("nextstart")

    def next(self):
        print("next")

    def stop(self):
        print("stop")

# 1. Create a cerebro
cerebro = bt.Cerebro(stdstats=False)
# 2. Add data feed
# 2.1  Create a data feed
dataframe = pd.read_csv(r'E:\project\backtrader_youtube_tutorial\demo\MES.csv')
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

brf_daily = bt.feeds.PandasData(dataname=dataframe)


# 2.2 Add the Data Feed to Cerebro
cerebro.adddata(brf_daily)

# 3. Add strategy
cerebro.addstrategy(MyStrategy)

# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Run over everything
cerebro.run()

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 5. Plot result
cerebro.plot()

