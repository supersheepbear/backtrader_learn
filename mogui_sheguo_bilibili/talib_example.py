"""
https://www.bilibili.com/video/BV1QA411x78Q
"""
import requests
import backtrader as bt
import pandas as pd
import json
import matplotlib.pyplot as plt
import datetime


class ULTOSCStrategy(bt.Strategy):
    params = (
        ('period_1', 7),
        ('period_2', 14),
        ('period_3', 28)
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.ULTOSC = bt.talib.ULTOSC(self.data.high, self.data.low, self.data.close,
                                      timeperiod1=self.params.period_1,
                                      timeperiod2=self.params.period_2,
                                      timeperiod3=self.params.period_3)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: {:.2f}, Cost: {:.2f}, Comm: {:.2f}'.format(
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm
                    )
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            else:
                self.log(
                    'SELL EXECUTED, Price: {:.2f}, Cost: {:.2f}, Comm: {:.2f}'.format(
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm
                    )
                )
                self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log("OPERATION PROFIT, GROSS {:.2f}, NET {:.2f}".format(trade.pnl, trade.pnlcomm))

    def next(self):
        if not self.position:
            if self.ULTOSC < 30:
                self.buy()
        elif self.ULTOSC > 70:
            self.close()


if __name__ == "__main__":
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

    cerebro = bt.Cerebro()

    cerebro.adddata(data)

    cerebro.addstrategy(ULTOSCStrategy)

    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.47, margin=1200.0, mult=5.0)

    print('start portfolio value {}'.format(cerebro.broker.get_value()))
    cerebro.run()
    print('end portfolio value {}'.format(cerebro.broker.get_value()))

    cerebro.plot(style='candle')

