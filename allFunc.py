import talib
from functools import reduce
from rqalpha.api import *
from rqalpha import run_func
import numpy as np
np.set_printoptions(suppress=True)

def SMA(vals, n, m):
    res = np.empty(shape=(vals.size)) * np.nan
    ct = 0
    ret = 0
    newct = 0
    while np.isnan(vals[newct]):
        newct = newct + 1

    while ct < (n - 1):
        ret = ret + vals[ct + newct]
        ct = ct + 1
    ret = ret / (n - 1)
    ct = ct + newct
    res.itemset(ct - 1, ret)
    while ct < vals.size:
        ret = (vals[ct] * m + ret * (n - m)) / n
        res.itemset(ct, ret)
        ct = ct + 1

    return res


# 指数平滑移动平均
#
# 算法
# Y = (X*2 + Y'*(N-1)) / (N+1)
#
# 或者 EMA(X, N) = SMA(X, N+1, 2)
def EMA(vals, n):
    return SMA(vals, n + 1, 2)


def MACD(vals, short, long, smooth):

    macd = EMA(vals, short) - EMA(vals, long)
    signal = EMA(macd, smooth)
    hist = np.subtract(macd,signal)

    res = (macd, signal,hist)
    return res


#########################################################################################
def main():
    SHORTPERIOD = 24
    LONGPERIOD = 52
    SMOOTHPERIOD = 9
    OBSERVATION = 100
    # init numpy nd array
    a = np.array([5.51083585, 5.42098526, 5.45093546, 5.54078604, 5.64062002, 5.68055362,
                  5.74045401, 5.71050381, 5.63063663, 5.49086905, 5.58071963, 5.54078604,
                  5.52081924, 5.59070303, 5.66058682, 5.60068643, 5.67057022, 5.72048721,
                  5.7504374, 5.89020498, 5.67057022, 5.7704042, 5.84028799, 5.82032119,
                  5.98005557, 6.01000576, 5.99, 6.12, 6.14, 6.24, 6.38,
                  6.42, 6.45, 6.57, 6.35, 6.22, 6.53, 6.59,
                  6.59, 6.44, 6.3, 6.25, 6.12, 6.43, 6.41,
                  6.46, 6.43, 6.48, 6.59, 6.52, 6.74, 6.84,
                  6.89, 6.71, 6.74, 6.55, 6.6, 6.7, 6.75,
                  6.96, 6.89, 6.96, 7.02, 7., 6.97, 7.08,
                  7., 6.78, 6.8, 6.77, 6.58, 6.61, 6.64,
                  6.79, 6.79, 6.87, 6.95, 7.14, 7.06, 6.92,
                  7.01, 7.05, 6.71, 6.7, 6.73, 6.8, 6.86,
                  7.07, 7.07, 7.26, 7.2, 7.26, 7.25, 7.3,
                  7.6, 7.57, 7.87, 7.73, 7.66, 7.5, 7.58,
                  7.64, 7.66, 7.64, 7.33, 7.32, 7.56, 7.69,
                  7.68, 7.94, 7.88, 7.83, 7.71, 7.73, 7.66,
                  7.49, 7.54, 7.14, 7.23, 6.93, 6.94])

    # test how talib SMA works
    # talib.EMA(a,12)
    sma_short = talib.EMA(a, 12)
    sma_long = talib.EMA(a, 26)
    #
    # print (sma_short)
    # print (sma_long)
    # print(sma_short-sma_long)

    # test how talib macd works
    macd, signal, hist = talib.MACD(a, SHORTPERIOD, LONGPERIOD, SMOOTHPERIOD)
    print(macd)

    # print(EMA(a, 12))

    print (MACD(a,SHORTPERIOD,LONGPERIOD,SMOOTHPERIOD)[0])

