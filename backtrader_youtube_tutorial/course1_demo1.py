"""
Use pandas datafeed to read data
"""
# -*- coding:utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import backtrader as bt
import pandas as pd


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

brf_daily = bt.feeds.PandasData(dataname=dataframe)


# 2.2 Add the Data Feed to Cerebro
cerebro.adddata(brf_daily)

# 3. Add strategy
cerebro.addstrategy(bt.Strategy)

# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Run over everything
cerebro.run()

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 5. Plot result
cerebro.plot()

