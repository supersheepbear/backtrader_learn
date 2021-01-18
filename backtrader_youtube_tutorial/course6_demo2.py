"""
An example of porfolio backtest
"""
# -*- coding:utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader as bt
import pandas as pd
import datetime


class HalfHalfStrategy(bt.Strategy):

    def __init__(self):
        pass

    def next(self):
        today = self.data.datetime.date()
        year, month = today.year, today.month

        if month == 12:
            this_month_length = (datetime.datetime(year+1, 1, 1) - datetime.datetime(year, month, 1)).days
        else:
            this_month_length = (datetime.datetime(year, month+1, 1) - datetime.datetime(year, month, 1)).days

        if today.day == this_month_length:
            self.order_target_percent(target=0.45, data="jpy")
            self.order_target_percent(target=0.45, data="cl")

    def stop(self):
        print("stop")


if __name__ == '__main__':
    # 1. Create a cerebro
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Value)

    # 2. Add data feed
    # 2.1  Create a data feed

    total_df = pd.read_hdf(r'processed_data.h5', key='data')
    for col_name in total_df.columns:
        dataframe = total_df[[col_name]]
        for col in ["open", "high", "low", "close"]:
            dataframe.loc[:, col] = dataframe.loc[:, col_name]
        dataframe["volume"] = 1
        datafeed = bt.feeds.PandasData(dataname=dataframe)

        # 2.2 Add the Data Feed to Cerebro
        cerebro.adddata(datafeed, name=col_name[0:-6])

    # 3. Add strategy
    cerebro.addstrategy(HalfHalfStrategy)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 5. Plot result
    cerebro.plot()
