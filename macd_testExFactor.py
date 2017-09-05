import talib
from rqalpha.api import *
from rqalpha import run_func
import numpy as np
import math
import allFunc as myfunc
import csv
import pandas as pd
# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    context.s1 = '600005.XSHG'

    # 使用MACD需要设置长短均线和macd平均线的参数
    context.SHORTPERIOD = 12
    context.LONGPERIOD = 26
    context.SMOOTHPERIOD = 9
    context.OBSERVATION = 100
    f = open('/Users/keli/Downloads/demo/' + context.s1 + '.csv', 'w')
    f.write('date')
    f.write(',')
    f.write('rq_adjusted_price')
    f.write(',')
    f.write('unadjusted_price')
    f.write('\n')

    context.file = f
    context.stock_history = pd.read_csv('/Users/keli/Documents/Quant/Stock_data/股票历史行情', sep='|')

# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑

    # current_date = bar_dict[context.s1].datetime.strftime('%Y-%m-%d')  # 可以拿到某个证券的bar信息

    #
    # exit(0)
    # context.portfolio 可以拿到现在的投资组合状态信息

    # 使用order_shares(id_or_ins, amount)方法进行落单

    # TODO: 开始编写你的算法吧！

    # 读取历史数据，使用sma方式计算均线准确度和数据长度无关，但是在使用ema方式计算均线时建议将历史数据窗口适当放大，结果会更加准确,OBSERVATION >=200
    prices = history_bars(context.s1, context.OBSERVATION, '1d', ['datetime', 'close'])
    # get_price(context.s1, start_date, end_date=None, frequency='1d', fields='close', adjust_type='pre',
    #           skip_suspended=False)
    for price in prices:
        curDate = str(price['datetime'])[:4] + '-' + str(price['datetime'])[4:6] + '-' + str(price['datetime'])[6:8]
        unadjusted_price = (context.stock_history.loc[(context.stock_history['stock_code'] == context.s1) & (
        context.stock_history['date'] == curDate)]['close'].values)[0]
        context.file.write(curDate)
        context.file.write(',')
        context.file.write(str(price['close']))
        context.file.write(',')
        context.file.write(str(unadjusted_price))
        context.file.write('\n')

    prices = prices['close']
    # with open('/Users/keli/Documents/Quant/600000.XSHG', 'w') as file:
    #         csv.writer(file).writerows(prices)
    # exit(0)
    # print (len(prices))


    # test how talib macd works
    # macd, signal, hist = talib.MACD(a, context.SHORTPERIOD, context.LONGPERIOD, context.SMOOTHPERIOD)

    # print("talib signal: ")
    # print(signal)
    #
    # res = MACD(prices, context.SHORTPERIOD, context.LONGPERIOD, context.SMOOTHPERIOD)
    # print("my signal: ")
    # print(res[1])



    # 用Talib计算MACD取值，得到三个时间序列数组，分别为macd, signal 和 hist
    macd, signal, hist = talib.MACD(prices, context.SHORTPERIOD,
                                    context.LONGPERIOD, context.SMOOTHPERIOD)
    # print (macd)

    # exit(0)

    # use my functions
    # macd, signal, hist =  myfunc.MACD(prices, context.SHORTPERIOD, context.LONGPERIOD, context.SMOOTHPERIOD)


    plot("macd", macd[-1])
    plot("macd signal", signal[-1])

    # macd 是长短均线的差值，signal是macd的均线，使用macd策略有几种不同的方法，我们这里采用macd线突破signal线的判断方法

    # 如果macd从上往下跌破macd_signal

    if macd[-1] - signal[-1] < 0 and macd[-2] - signal[-2] > 0:
        # 计算现在portfolio中股票的仓位
        curPosition = context.portfolio.positions[context.s1].quantity
        # 进行清仓
        if curPosition > 0:
            order_target_value(context.s1, 0)

    # 如果短均线从下往上突破长均线，为入场信号
    if macd[-1] - signal[-1] > 0 and macd[-2] - signal[-2] < 0:
        # 满仓入股
        order_target_percent(context.s1, 1)

    print(context.portfolio.daily_pnl)


config = {
    "base": {
        "start_date": "2011-06-27",
        "end_date": "2011-06-27",
        "benchmark": "000001.XSHG",
        "accounts": {
            "stock": 100000
        }
    }
    ,
    # "extra": {
    #   "log_level": "verbose",
    # },
    "mod": {
        "sys_analyser": {
            # "enabled": False,
            "plot": False
        }
    }
}

# 您可以指定您要传递的参数
run_func(init=init, handle_bar=handle_bar, config=config)
