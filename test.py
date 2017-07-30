from rqalpha.api import *
# run_func_demo
from rqalpha.api import *
from rqalpha import run_func
import numpy
import csv

def init(context):
    logger.info("init")

def before_trading(context, bar_dict):
    pass
def handle_bar(context, bar_dict):
    # getInstruments()
    getDividend()





def getDividend():#日期不能为none，notebook里可以
    fname = "/Users/keli/Documents/Quant/orderBookList"
    with open(fname) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    for order_book_id in content:
        dividendFile = '/Users/keli/Documents/Quant/Stock_data/dividend1/' + order_book_id + '_dividend'
        # with open(dividendFile, 'a') as f:
        #     f.write(
        #         'announcement_date|book_closure_date|ex_dividend_date|payable_date|dividend_cash_before_tax|round_lot')
        #     f.write('\n')
        # f.close()

        print (order_book_id)
        try:
            a = get_dividend(order_book_id, start_date='2004-01-01', end_date='2017-07-01', adjusted=None, country='cn')
        except:
            print (order_book_id + " is invalid instrument")
            pass
        if a is None or len(a) == 0:
            print (order_book_id + ' has no data')
        else:
            numpy.savetxt(dividendFile, a, delimiter="|",fmt='%s')

        # print (a.dtype.names)
        # print (a.__class__.__name__)



def getInstruments():
    fname = "/Users/keli/Documents/Quant/orderBookList"
    with open(fname) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    delimiter = '|'
    allInstruments = instruments(content)
    with open('/Users/keli/Documents/Quant/instruments', 'w') as file:
        file.write(
            'order_book_id|symbol|abbrev_symbol|round_lot|sector_code|sector_code_name|industry_code|industry_name'
            '|listed_date|de_listed_date|type|concept_names|exchange|board_type|status|special_type')
        file.write('\n')
        for ins in allInstruments:
            print (ins.order_book_id)
            file.write(ins.order_book_id)
            file.write(delimiter)
            file.write(ins.symbol)
            file.write(delimiter)
            file.write(ins.abbrev_symbol)
            file.write(delimiter)
            file.write(str(ins.round_lot))
            file.write(delimiter)
            file.write(ins.sector_code)
            file.write(delimiter)
            file.write(ins.sector_code_name)
            file.write(delimiter)
            file.write(ins.industry_code)
            file.write(delimiter)
            file.write(ins.industry_name)
            file.write(delimiter)
            file.write(str(ins.listed_date))
            file.write(delimiter)
            file.write(str(ins.de_listed_date))
            file.write(delimiter)
            file.write(ins.type)
            file.write(delimiter)
            file.write(ins.concept_names)
            file.write(delimiter)
            file.write(ins.exchange)
            file.write(delimiter)
            file.write(ins.board_type)
            file.write(delimiter)
            file.write(ins.status)
            file.write(delimiter)
            file.write(ins.special_type)
            file.write('\n')
    file.close()
config = {
  "base": {
    "start_date": "2017-06-01",
    "end_date": "2017-06-01",
    "benchmark":None,
    "accounts": {
        "stock": 22
    }
  }
    # ,
  # "extra": {
  #   "log_level": "verbose",
  # },
  # "mod": {
  #   "sys_analyser": {
  #     "enabled": False,
  #     "plot": False
  #   }
  # }
}

# 您可以指定您要传递的参数
run_func(init=init, before_trading=before_trading, handle_bar=handle_bar, config=config)

# 如果你的函数命名是按照 API 规范来，则可以直接按照以下方式来运行
# run_func(**globals())