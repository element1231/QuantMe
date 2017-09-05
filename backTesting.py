import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import talib

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

np.set_printoptions(suppress=True)
stock = '600007.XSHG'
start_date = '2015-05-30'
end_date = '2017-07-01'

account = 100000
SHORTPERIOD = 12
LONGPERIOD = 26
SMOOTHPERIOD = 9
OBSERVATION = 200

cur_date = start_date
quantity = 0

daily_pnl = 0.0

buy_fee_rate = 0.0008
sell_fee_rate = 0.0018
last_close = 0.0
last_ttl = account
ttl = 0
dividend_cash = 0.0
stock_history = pd.read_csv('/Users/keli/Documents/Quant/Stock_data/股票历史行情', sep='|')
split_data = pd.read_csv('/Users/keli/Documents/Quant/Stock_data/拆分数据', sep='|')
ex_factor_data = pd.read_csv('/Users/keli/Documents/Quant/Stock_data/复权因子', sep='|')
dividend_data = pd.read_csv('/Users/keli/Documents/Quant/Stock_data/分红数据', sep='|')

while (cur_date <= end_date):
    first_date = (datetime.strptime(cur_date, '%Y-%m-%d') - timedelta(days=OBSERVATION * 2)).strftime('%Y-%m-%d')
    # print('#############################')
    # print('cur_date: ' + cur_date)

    prices = []
    fired = False
    sell = False
    fee = 0.0
    obser_dates = []
    ex_factor = []
    split = 1

    isTradingDay = False

    trading_dates = stock_history.loc[stock_history['stock_code'] == stock]['date'].values  # ndarray

    if cur_date in trading_dates:
        isTradingDay = True
        cur_history = stock_history.loc[(stock_history['date'] > first_date) & (stock_history['date'] <= cur_date) & (
            stock_history['stock_code'] == stock)]  # dataframe
        obser_dates = cur_history['date'].values  # ndarray
        prices = cur_history['close'].values
    if not isTradingDay:
        # print('current date is not a trading day: ' + cur_date)
        cur_date = (datetime.strptime(cur_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        continue


    print(cur_date)


    cur_ex_factor_data = ex_factor_data.loc[(ex_factor_data['order_book_id'] == stock)]
    cur_split_data = split_data.loc[(split_data['stock_code'] == stock)]
    cur_dividend_data= dividend_data.loc[(dividend_data['stock_code'] == stock)]

    if quantity > 0:
        for row in cur_dividend_data.itertuples():
            if cur_date == row[5]:
                round_lot = row[6]
                dividend = row[3]
                cur_dividend_cash =  quantity/round_lot * dividend
                account = account + cur_dividend_cash
                dividend_cash = dividend_cash + cur_dividend_cash
                # print ("get dividend: ", dividend_cash)
        for row in cur_split_data.itertuples():

            if cur_date == row[1]:
                split = row[5] / row[4]
                quantity = quantity * split
                # print("quantity changed: ", quantity)
                break
    obser_dates = np.array(obser_dates)[len(obser_dates) - OBSERVATION:]
    prices = np.array(prices)[len(prices) - OBSERVATION:]

    for row in cur_ex_factor_data.itertuples():
        if obser_dates[0] < row[1] and row[1] <= cur_date:
            for obser_date in obser_dates:
                if obser_date < row[1]:
                    ex_factor.append(row[3])
                elif obser_date >= row[1]:
                    ex_factor.append(1)

            prices = prices / ex_factor
            ex_factor = np.array(ex_factor)[len(ex_factor) - OBSERVATION:]
            break

    close = prices[-1]

    macd, signal, hist = talib.MACD(prices, SHORTPERIOD, LONGPERIOD, SMOOTHPERIOD)

    if macd[-1] - signal[-1] < 0 and macd[-2] - signal[-2] > 0:
        # 进行清仓
        if quantity > 0:
            fee = close * quantity * sell_fee_rate
            account = account + close * quantity - fee
            sell = True
            # print('sell quantity: ', quantity)
            quantity = 0
            market_value = quantity * close
            ttl = account + market_value - dividend_cash
            daily_pnl = ttl - last_ttl

            # print('account cash: ', account)
            # print('sell fee: ', fee)
            # print('market value: ', market_value)
            # print("daily pnl: ", daily_pnl)
            print (daily_pnl)
            # print("quantity: ", quantity)
            # 如果短均线从下往上突破长均线，为入场信号
    if macd[-1] - signal[-1] > 0 and macd[-2] - signal[-2] < 0:
        # 满仓入股
        if account >= (close * 100):
            quantity = account / close
            # quantity = int(round(quantity / 100, 2)) * 100
            quantity = float(truncate(quantity / 100, 0)) * 100
            fee = close * quantity * buy_fee_rate
            account = account - close * quantity - fee
            fired = True
            market_value = quantity * close
            ttl = account + market_value - dividend_cash
            daily_pnl = ttl - last_ttl

            # print('bought quantity: ', quantity)
            # print('account cash: ', account)
            # print('buy fee: ', fee)
            # print('market value: ', market_value)
            # print("daily pnl: ", daily_pnl)
            print(daily_pnl)
            # print("quantity: ", quantity)
    if not fired and not sell > 0:
        market_value = quantity * close

        ttl = account + market_value - dividend_cash
        daily_pnl = ttl - last_ttl

        # print('account cash: ', account)
        # print('market value: ', market_value)
        # print("daily pnl: ", daily_pnl)
        print(daily_pnl)
        # print ("quantity: ", quantity)
    last_ttl = ttl
    last_close = close
    cur_date = (datetime.strptime(cur_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

print('done')
