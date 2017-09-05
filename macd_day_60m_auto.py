import talib
from datetime import *
import pandas as pd
import numpy as np
from rqalpha.api import *
from rqalpha import run_func


def init(context):
    list = read_delete_line_from_file()
    context.filename1d = str(list[0])
    context.filename60m = str(list[1])
    context.path1d = '/Users/keli/Documents/Quant/Stock_data/100SHEstockprices_1d'
    context.path60m = '/Users/keli/Documents/Quant/Stock_data/100SHEstockprices_60m'

    context.s1 = str(list[0]).split('_')[2]
    print(context.s1)
    exit(0)

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
            # order_percent(context.s1, 1)
            macd_60m(context, bar_dict)

        if hist[-1] > 0 and context.last > 0 and abs(hist[-1]) < abs(context.last):
            print (
            "@@@@@@@@@@ sell signal - hist is above the axis and current hist is less than previous hist @@@@@@@@@@")
            # print ("current hist: %s " % (str(2 * hist[-1])))
            # print ("previous hist: %s " % (str(2 * context.last)))
            # print("prices: ",prices)
            print (end_date)
            # macd_60m(context,bar_dict)

            order_percent(context.s1, -1)

        elif hist[-1] < 0 and context.last < 0 and abs(hist[-1]) < abs(context.last):
            print (
            "@@@@@@@@@@ buy signal - hist is below the axis and current hist is larger than previous hist @@@@@@@@@@")
            # print ("current hist: %s " % (str(2 * hist[-1])))
            # print ("previous hist: %s " % (str(2 * context.last)))
            print(end_date)
            macd_60m(context, bar_dict)
            # if context.portfolio.cash > prices[-1] * 100:
            #     print(context.portfolio)
            #     print("place order")
            #     order_value(context.s1, context.portfolio.cash)
            # else:
            #     print("skip order, no money")
        context.last = hist[-1]



# def after_trading(context):
#     print ("done")

def calTime(original_datetime,delta):
    return (datetime.strptime(original_datetime, '%Y-%m-%d') + timedelta(days=delta)).strftime('%Y-%m-%d')

def macd_60m(context,bar_dict):
    price_60 = pd.read_csv('/Users/keli/Documents/Quant/Stock_data/price_pre_600888_60m2', sep='|')
    cur_date = (bar_dict[context.s1].datetime.strftime('%Y-%m-%d'))
    previous_date = calTime(cur_date,-1)
    last_date = calTime(cur_date,+1)
    first_date = calTime(previous_date,-100)

    previous_price_history = price_60.loc[
        (price_60['date'] >= first_date) & (price_60['date'] < cur_date) & (
            price_60['stock_code'] == context.s1)]['close'].values  # dataframe
    previous_price_history = np.array(previous_price_history)[len(previous_price_history) - 200:]
    hist_60 = talib.MACD(previous_price_history, 12, 26, 9)[2]

    last_hist = hist_60[-1]
    rops = price_60.loc[
        (price_60['date'] >= cur_date) & (price_60['date'] < last_date) & (
            price_60['stock_code'] == context.s1)]['date'].values
    # print ("rops: ", rops)
    for i in range(len(rops)):
        print ("current rop: ", rops[i])
        previous_price_history = price_60.loc[
            (price_60['date'] >= first_date) & (price_60['date'] <= rops[i]) & (
                price_60['stock_code'] == context.s1)]['close'].values
        previous_price_history = np.array(previous_price_history)[len(previous_price_history) - 200:]
        hist_60 = talib.MACD(previous_price_history, 12, 26, 9)[2]
        if hist_60[-1] < 0 and last_hist > 0:
            print("@@@@@@@@@@ 60m sell signal - hist is moving up->down across the axis @@@@@@@@@@")
            # print ("current hist: %s " % (str(2 * hist[-1])))
            # print ("previous hist: %s " % (str(2 * context.last)))
            order_percent(context.s1, -1)
            # last_hist = hist_60[-1]
        elif hist_60[-1] > 0 and last_hist < 0:
            print("@@@@@@@@@@ 60m buy signal - hist is moving down->up across the axis @@@@@@@@@@")
            # print ("current hist: %s " % (str(2 * hist[-1])))
            # print ("previous hist: %s " % (str(2 * context.last)))
            # print(end_date)
            if context.portfolio.cash > previous_price_history[-1] * 100:

                print("place order")
                # order_value(context.s1, context.portfolio.cash)
                order_percent(context.s1, 1)
                print(context.portfolio)
            else:
                print("skip order, no money")
            # last_hist = hist_60[-1]
        elif hist_60[-1] > 0 and last_hist > 0 and abs(hist_60[-1]) < abs(last_hist):
            print(
                "@@@@@@@@@@ 60m sell signal - hist is above the axis and current hist is less than previous hist @@@@@@@@@@")
            # print("current hist: %s " % (str(2 * hist_60[-1])))
            # print("previous hist: %s " % (str(2 * last_hist)))
            # print("prices: ", previous_price_history)
            print("sell")
            order_percent(context.s1, -1)
            # last_hist = hist_60[-1]

        elif hist_60[-1] < 0 and last_hist < 0 and abs(hist_60[-1]) < abs(last_hist):
            print(
                "@@@@@@@@@@ 60m buy signal - hist is below the axis and current hist is larger than previous hist @@@@@@@@@@")
            # print("current hist: %s " % (str(2 * hist_60[-1])))
            # print("previous hist: %s " % (str(2 * last_hist)))
            if context.portfolio.cash > previous_price_history[-1] * 100:
                print("place order")
                # order_value(context.s1, context.portfolio.cash)
                order_percent(context.s1, 1)
                print(context.portfolio)
            else:
                print("skip order, no money")
        last_hist = hist_60[-1]
    # macd_60, signal_60, hist_60 = talib.MACD(prices_60m, 12, 26, 9)
    # print(2 * hist_60[-1])


def read_delete_line_from_file():
    f = open("/Users/keli/Documents/Quant/Stock_data/fileList", "r")
    lines = f.read().splitlines()
    # print(lines)
    f.close()
    list = []
    f = open("/Users/keli/Documents/Quant/Stock_data/fileList", "w")
    for i in range(len(lines)):
        if i == 0 or i == 1:
            # print('append ', lines[i])
            list.append(lines[i])
        else:
            f.write(lines[i] + "\n")
    f.close()
    return list

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