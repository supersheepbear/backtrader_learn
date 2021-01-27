"""
https://www.bilibili.com/video/BV1qp4y1s7Kw
"""
import backtrader as bt
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import backtrader.analyzers as btanalyzers
import math
import numpy as np
#import quantstats as qs


class RVI(bt.Indicator):
    lines = ('std', 'pos', 'neg', 'rvi')
    plotlines = dict(
        std=dict(_plotskip=True),
        pos=dict(_plotskip=True),
        neg=dict(_plotskip=True),
        rvi=dict(_plotskip=False),
    )

    params = (
        ('period', 20),
    )

    def __init__(self):
        self.lines.std = bt.talib.STDDEV(self.datas[0].close, timeperiod=10, nbdev=2.0)

    def next(self):
        if self.lines.std[0] > self.lines.std[-1]:
            self.lines.pos[0] = self.lines.std[0]
        else:
            self.lines.pos[0] = 0

        if self.lines.std[0] < self.lines.std[-1]:
            self.lines.neg[0] = self.lines.std[0]
        else:
            self.lines.neg[0] = 0

        pos_nan = np.nan_to_num(self.lines.pos.get(size=self.params.period))
        neg_nan = np.nan_to_num(self.lines.neg.get(size=self.params.period))

        Usum = math.fsum(pos_nan)
        Dsum = math.fsum(neg_nan)

        if (Usum + Dsum) == 0:
            self.lines.rvi[0] = 0
            return

        self.lines.rvi[0] = 100 * Usum/(Usum + Dsum)


class RVIStrategy(bt.Strategy):
    params = ()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.rvi = RVI()

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
        up = 60
        down = 35
        szie_1 = math.floor(cerebro.broker.get_cash()*0.9 / self.datas[0].close[0])
        if not self.position:
            if self.rvi.rvi[0] > up:
                if self.rvi.rvi[-1] < up and self.rvi.rvi[-2] < up:
                    self.order_target_percent(target=0.9)
                    #self.order = self.buy(size=szie_1, exectype=bt.Order.StopTrail, trailpercent=0.11)
        else:
            if self.rvi.rvi[0] < down:
                if self.rvi.rvi[-1] > down and self.rvi.rvi[-2] > down:
                    for data in self.datas:
                        size = self.getposition(data).size
                        if size != 0:
                            self.close(data)


if __name__ == "__main__":
    cerebro = bt.Cerebro(stdstats=False)

    SP = bt.feeds.YahooFinanceData(dataname='^GSPC',
                                   fromdate=datetime.datetime(2011, 1, 1),
                                   todate=datetime.datetime(2020, 12, 4))
    cerebro.adddata(SP)

    cerebro.addstrategy(RVIStrategy)

    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    # Add observers
    # cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell)
    # cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.Value)
    #cerebro.addobserver(bt.observers.TimeReturn)
    cerebro.addobserver(bt.observers.Benchmark,
                        data=SP,
                        timeframe=bt.TimeFrame.Years)


    # Add analyser
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')  # 加入PyFolio分析者
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    # cerebro.addanalyzer(bt.analyzers.Transactions)

    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    results = cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 5. Plot result
    cerebro.plot(style='candle', iplot=False)

    strat = results[0]  # 获得策略实例

    portfolio_stats = strat.analyzers.getbyname('PyFolio')  # 得到PyFolio分析者实例
    # 以下returns为以日期为索引的资产日收益率系列
    returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()

    returns.index = returns.index.tz_convert(None)  # 索引的时区要设置一下，否则出错

    # 输出html策略报告,rf为无风险利率
    #qs.reports.html(returns, output='stats.html', title='策略绩效报告', rf=0.0)
