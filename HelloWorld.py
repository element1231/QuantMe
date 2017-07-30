import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import talib
np.set_printoptions(suppress=True)
stock='000001.XSHE'
start_date='2016-06-15'
end_date='2016-07-01'

fired=False
account = 100000
SHORTPERIOD = 12
LONGPERIOD = 26
SMOOTHPERIOD = 9
OBSERVATION = 200
first_date = (datetime.strptime(start_date,'%Y-%m-%d') - timedelta(days=OBSERVATION*2)).strftime('%Y-%m-%d')
print (start_date)
print (first_date)

# prices = np.empty(shape=(OBSERVATION*2)) * np.nan

prices = []

# prices = history_bars(context.s1, context.OBSERVATION, '1d', 'close')
if not fired:
    fired = True
df = pd.read_csv('/Users/keli/Documents/Quant/Stock_data/股票历史行情', sep='|')
# res = pd.DataFrame(columns=['date', 'stock_code', 'close'])

# ct = 0
for row in df.itertuples():
    if row.date > first_date and row.date<=start_date and row.stock_code==stock:
        prices.append(row.close)
        # print (row)
        # res = res.append({'date':row.date,'stock_code':row.stock_code,'close':row.close},ignore_index = True)

prices = np.array(prices)[len(prices)-OBSERVATION:len(prices)]

macd, signal, hist = talib.MACD(prices, SHORTPERIOD,LONGPERIOD, SMOOTHPERIOD)

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

# print (res)
# print (prices)
print ('done')
