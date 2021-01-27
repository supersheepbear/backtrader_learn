"""
https://www.bilibili.com/video/BV1QA411x78Q
"""
import requests
import backtrader as bt
import pandas as pd
import json
import matplotlib.pyplot as plt
import datetime
#import quantstats as qs
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo


class ULTOSCStrategy(bt.Strategy):
    params = (
        ('period_1', 3),
        ('period_2', 7),
        ('period_3', 18)
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.ULTOSC = bt.talib.ULTOSC(self.data.high, self.data.low, self.data.close,
                                      timeperiod1=self.params.period_1,
                                      timeperiod2=self.params.period_2,
                                      timeperiod3=self.params.period_3)
        self.SP = self.data1.close

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
                if self.SP[0] > self.SP[-1]:
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

    cerebro = bt.Cerebro()

    data = bt.feeds.YahooFinanceData(dataname='TSLA',
                                     fromdate=datetime.datetime(2011, 1, 1),
                                     todate=datetime.datetime(2020, 12, 4))
    cerebro.adddata(data)
    SP = bt.feeds.YahooFinanceData(dataname='^GSPC',
                                   fromdate=datetime.datetime(2011, 1, 1),
                                   todate=datetime.datetime(2020, 12, 4))
    cerebro.adddata(SP)

    # cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell)
    # cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.Value)
    cerebro.addobserver(bt.observers.TimeReturn)

    # Add analyser
    #cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')  # 加入PyFolio分析者
    cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)

    cerebro.addstrategy(ULTOSCStrategy)

    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=10)

    print('start portfolio value {}'.format(cerebro.broker.get_value()))
    results = cerebro.run()
    print('end portfolio value {}'.format(cerebro.broker.get_value()))

    strat = results[0]  # 获得策略实例

    #b = Bokeh(style='bar') # 黑底, 单页
    #b = Bokeh(style='bar', tabs='multi') # 黑底, 多页
    #b = Bokeh(style='bar', scheme=Tradimo()) # 传统白底, 单页
    #b = Bokeh(style='bar', tabs='multi', scheme=Tradimo()) # 传统白底, 多页
    cerebro.plot(style='candle')
