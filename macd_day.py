import talib
from datetime import *
import pandas as pd
import numpy as np
from rqalpha.api import *
from rqalpha import run_func


def init(context):
    context.s1 = "600888.XSHG"
    logger.info("RunInfo: {}".format(context.run_info))
    context.first_time = True
    context.last = 0
    context.stock_price =  pd.read_csv('/Users/keli/Documents/Quant/Stock_data/price_pre_600888_day2', sep='|')

    # context.price_60 = price_60
def before_trading(context):
    pass


def handle_bar(context, bar_dict):
    end_date = bar_dict[context.s1].datetime.strftime('%Y-%m-%d')
    start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(
        days=400)).strftime('%Y-%m-%d')


    print("start_date: %s " % start_date)
    print("end_date: %s " % end_date)
    stock_history = context.stock_price

    # # check suspend
    # if stock_history.loc[(stock_history['date'] == end_date)].empty:
    #     print("suspend happens on %s " % end_date)
    #     return

    # stock_history = pd.read_csv('/Users/keli/Documents/Quant/Stock_data/price_pre', sep='|')
    prices = stock_history.loc[(stock_history['date'] >= start_date) & (stock_history['date'] <= end_date) & (
        stock_history['stock_code'] == context.s1)]['close'].values

    prices = np.array(prices)[len(prices) - 200:]

    macd, signal, hist = talib.MACD(prices, 12, 26, 9)

    # print ("history hist: ",2 * hist[-1])

    if context.first_time:
        context.last = hist[-1]
        context.first_time = False
    else:
        if hist[-1] < 0 and context.last > 0:
            print ("@@@@@@@@@@ sell signal - hist is moving up->down across the axis @@@@@@@@@@")
            # print ("current hist: %s " % (str(2 * hist[-1])))
            # print ("previous hist: %s " % (str(2 * context.last)))
            print(end_date)
            order_percent(context.s1, -1)

        elif hist[-1] > 0 and context.last < 0:
            print ("@@@@@@@@@@ buy signal - hist is moving down->up across the axis @@@@@@@@@@")
            # print ("current hist: %s " % (str(2 * hist[-1])))
            # print ("previous hist: %s " % (str(2 * context.last)))
            # print(end_date)
            if context.portfolio.cash > prices[-1] * 100:
                print(context.portfolio)
                print("place order")
                order_percent(context.s1, 1)
            else:
                print("skip order, no money")

        if hist[-1] > 0 and context.last > 0 and abs(hist[-1]) < abs(context.last):
            print (
            "@@@@@@@@@@ sell signal - hist is above the axis and current hist is less than previous hist @@@@@@@@@@")
            # print ("current hist: %s " % (str(2 * hist[-1])))
            # print ("previous hist: %s " % (str(2 * context.last)))
            # print("prices: ",prices)
            print (end_date)
            order_percent(context.s1, -1)

        elif hist[-1] < 0 and context.last < 0 and abs(hist[-1]) < abs(context.last):
            print (
            "@@@@@@@@@@ buy signal - hist is below the axis and current hist is larger than previous hist @@@@@@@@@@")
            # print ("current hist: %s " % (str(2 * hist[-1])))
            # print ("previous hist: %s " % (str(2 * context.last)))
            print(end_date)
            if context.portfolio.cash > prices[-1] * 100:
                print(context.portfolio)
                print("place order")
                order_percent(context.s1, 1)
            else:
                print("skip order, no money")
        context.last = hist[-1]



# def after_trading(context):
#     print ("done")





config = {
  "base": {
    "start_date": "2016-08-01",
    "end_date": "2017-07-14",
    "benchmark": "000300.XSHG",
    "accounts": {
        "stock": 1000000
    }
  },
  "extra": {
    "log_level": "verbose",
  },
  "mod": {
    "sys_analyser": {
      "enabled": True,
      "plot": True
    }
  }
}

run_func(init=init, handle_bar=handle_bar, config=config)