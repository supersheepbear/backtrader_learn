"""
Dualrust strategy optimization
"""
# -*- coding:utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader as bt
import pandas as pd
import datetime


class DT_Line(bt.Indicator):
    lines = ('U', 'D')
    params = (('period', 2), ('k_u', 0.7), ('k_d', 0.7))

    def __init__(self):
        self.addminperiod(self.p.period + 1)

    def next(self):
        HH = max(self.data.high.get(-1, size=self.p.period))
        LC = min(self.data.close.get(-1, size=self.p.period))
        HC = max(self.data.close.get(-1, size=self.p.period))
        LL = min(self.data.low.get(-1, size=self.p.period))
        R = max(HH - LC, HC - LL)
        self.lines.U[0] = self.data.open[0] + self.p.k_u * R
        self.lines.D[0] = self.data.open[0] - self.p.k_d * R


class DualRust(bt.Strategy):
    params = (('period', 2), ('k_u', 0.7), ('k_d', 0.7))

    def __init__(self):
        # do not plot the second data(day bar data)
        # self.data1.plotinfo.plot = False
        # For convenience
        self.dataclose = self.data0.close
        self.D_Line = DT_Line(self.data1, period=self.params.period, k_u=self.p.k_u, k_d=self.p.k_d)
        # plot d line on minute bar data
        # D_line frequency is day. The following line will make it become minute bar
        self.D_Line = self.D_Line()
        self.D_Line.plotinfo.plotmaster = self.data0

        self.buy_signal = bt.indicators.CrossOver(self.dataclose, self.D_Line.U)
        self.sell_signal = bt.indicators.CrossDown(self.dataclose, self.D_Line.D)

    def start(self):
        #print('start')
        pass

    def prenext(self):
        #print("prenext")
        pass

    def nextstart(self):
        #print("nextstart")
        pass

    def next(self):
        # do not hold position to the second day
        if self.data.datetime.time() < datetime.time(15, 55) or self.datetime.time() > datetime.time(17, 5):
            if not self.position and self.buy_signal[0] == 1:
                self.order = self.buy()
            if not self.position and self.sell_signal[0] == 1:
                self.order = self.sell()

            if self.getposition().size < 0 and self.buy_signal[0] == 1:
                self.order = self.close()
                self.order = self.buy()

            if self.getposition().size > 0 and self.sell_signal[0] == 1:
                self.order == self.close()
                self.order = self.sell()
        else:
            if self.position:
                self.order = self.close()

    def stop(self):
        print(
            'period: {}, k_u:{}, k_d:{}, final_value:{:.2f}'.format(
                self.p.period, self.p.k_u, self.p.k_d, self.broker.get_value()
            )
        )


if __name__ == '__main__':
    # 1. Create a cerebro
    cerebro = bt.Cerebro()
    # 2. Add data feed
    # 2.1  Create a data feed

    dataframe = pd.read_csv(r'MES_minute.csv')

    dataframe['datetime'] = pd.to_datetime(dataframe['datetime'], format='%Y-%m-%d %H:%M:%S')
    dataframe = dataframe.sort_values("datetime")
    dataframe.set_index('datetime', inplace=True)


    data = bt.feeds.PandasData(dataname=dataframe,
                               fromdate=datetime.datetime(2019, 5, 1),
                               todate=datetime.datetime(2019, 6, 1),
                               timeframe=bt.TimeFrame.Minutes)


    # 2.2 Add the Data Feed to Cerebro
    cerebro.adddata(data)
    # Resampled data will be data1 in cerebro
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Days)

    # 3. Add strategy
    cerebro.optstrategy(
        DualRust,
        period=range(1, 5), k_u=[n / 10.0 for n in range(2, 10)], k_d=[n / 10.0 for n in range(2, 10)]
    )

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 5. Plot result
    #cerebro.plot(style='candle')