import hbshare as hbs
import pandas as pd
import time
from MorningStarStyleBox import MorningStarStyleCalculator


def load_calendar(start_date, end_date):
    sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
        start_date, end_date)
    res = hbs.db_data_query('readonly', sql_script, page_size=5000)
    df = pd.DataFrame(res['data']).rename(
        columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                 "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
    df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)
    date_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()
    date_list = [x for x in date_list if x[4:6] in ['01', '04', '07', '08', '10']]

    return date_list


if __name__ == '__main__':
    date_l = load_calendar('20190101', '20210730')
    date = '20210730'
    mode = "all"
    t0 = time.time()
    label_result = MorningStarStyleCalculator(date, mode).get_construct_results()
    t1 = time.time()
    label_result['equity_score'].to_csv('D:\\kevin\\基金风格箱历史数据\\股票风格\\{}_{}.csv'.format(date, mode))
    label_result['fund_score'].to_csv('D:\\kevin\\基金风格箱历史数据\\基金风格\\{}_{}.csv'.format(date, mode))

    print("计算耗时: {} s".format(t1 - t0))