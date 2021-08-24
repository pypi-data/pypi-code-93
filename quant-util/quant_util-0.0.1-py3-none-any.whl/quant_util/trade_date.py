import akshare as ak
import datetime
import pandas as pd

trade_date_list = ak.tool_trade_date_hist_sina()['trade_date'].to_list()
trade_date_list = [i.strftime("%Y-%m-%d") for i in trade_date_list]
print(trade_date_list)


def standard_date_to_str(date):
    if date == 'now' or date == 'today':
        date = datetime.datetime.now()
    return pd.to_datetime(date).strftime("%Y-%m-%d")


def get_trade_date_list_by_range(start, end):
    sh_sz_trade_list = trade_date_list
    start = standard_date_to_str(start)
    end = standard_date_to_str(end)
    if start > end:
        return None
    """
    explanation:
       给出交易具体时间

    params:
        * start->
            含义: 开始日期
            类型: date
            参数支持: []
        * end->
            含义: 截至日期
            类型: date
            参数支持: []
    """
    start, end = get_real_datelist(sh_sz_trade_list, start, end)
    if start is not None:
        return sh_sz_trade_list[
               sh_sz_trade_list.index(start): sh_sz_trade_list.index(end) + 1: 1
               ]
    else:
        return None


def get_real_datelist(datelist, start, end):
    """
    explanation:
        取数据的真实区间，当start end中间没有交易日时返回None, None,
        同时返回的时候用 start,end=QA_util_get_real_datelist

    params:
        * start->
            含义: 开始日期
            类型: date
            参数支持: []
        * end->
            含义: 截至日期
            类型: date
            参数支持: []
    """
    real_start = get_real_date(start, datelist, 1)
    real_end = get_real_date(end, datelist, -1)
    if datelist.index(real_start) > datelist.index(real_end):
        return None, None
    else:
        return (real_start, real_end)


def get_real_date(date, trade_list, towards=-1):
    """
    explanation:
        获取真实的交易日期

    params:
        * date->
            含义: 日期
            类型: date
            参数支持: []
        * trade_list->
            含义: 交易列表
            类型: List
            参数支持: []
        * towards->
            含义: 方向， 1 -> 向前, -1 -> 向后
            类型: int
            参数支持: [1， -1]
    """
    date = str(date)[0:10]
    if towards == 1:
        if pd.Timestamp(date) >= pd.Timestamp(trade_list[-1]):
            return trade_list[-1]
        while date not in trade_list:
            date = str(
                datetime.datetime.strptime(str(date)[0:10], "%Y-%m-%d")
                + datetime.timedelta(days=1)
            )[0:10]
        else:
            return str(date)[0:10]
    elif towards == -1:
        if pd.Timestamp(date) <= pd.Timestamp(trade_list[0]):
            return trade_list[0]
        while date not in trade_list:
            date = str(
                datetime.datetime.strptime(str(date)[0:10], "%Y-%m-%d")
                - datetime.timedelta(days=1)
            )[0:10]
        else:
            return str(date)[0:10]
