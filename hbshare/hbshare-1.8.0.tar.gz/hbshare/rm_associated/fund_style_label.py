"""
基金风格标签模块
"""
import pandas as pd
import hbshare as hbs


class FundStyleLabelCalculator:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    @staticmethod
    def fetch_data_batch(user_name, sql_script):
        total_res = hbs.db_data_query(user_name, sql_script, is_pagination=False)
        n = total_res['pages']
        all_data = []
        for i in range(1, n + 1):
            res = hbs.db_data_query(
                user_name, sql_script, page_num=i, is_pagination=True, page_size=total_res['pageSize'])
            all_data.append(pd.DataFrame(res['data']))
        all_data = pd.concat(all_data)

        return all_data

    def _load_data(self):
        # mutual
        db_name = 'st_fund'
        user_name = 'funduser'
        sql_script = "SELECT * FROM {}.r_st_nav_attr_df where " \
                     "attr_type in ('style_allo', 'sector') and tjrq >= {} and data_type = '{}'".format(
                      db_name, self.start_date, 'r_square')
        data = self.fetch_data_batch(user_name, sql_script)
        data = data[['tjrq', 'jjdm', 'attr_type', 'data_type', 'style_factor', 'data_value']].rename(
            columns={"tjrq": "trade_date", "jjdm": "fund_id"})
        tmp = data.groupby(['trade_date', 'fund_id'])['data_type'].value_counts().reset_index(level=[0, 1]).reset_index(
            drop=True)
        tmp = tmp[tmp['data_type'] == 1]
        tmp = pd.pivot_table(tmp, index='trade_date', columns='fund_id', values='data_type').sort_index()
        # private
        # db_name = 'st_hedge'
        # user_name = 'highuser'
        # sql_script = "SELECT * FROM {}.r_st_nav_attr_df where " \
        #              "attr_type in ('style_allo', 'sector') and tjrq >= {} and data_type = '{}'".format(
        #               db_name, self.start_date, 'r_square')
        # data = self.fetch_data_batch(user_name, sql_script)
        # data = data[['tjrq', 'jjdm', 'attr_type', 'data_type', 'style_factor', 'data_value']].rename(
        #     columns={"tjrq": "trade_date", "jjdm": "fund_id"})
        # tmp = data.groupby(['trade_date', 'fund_id'])['data_type'].value_counts().reset_index(level=[0, 1]).reset_index(
        #     drop=True)
        # tmp = tmp[tmp['data_type'] == 1]
        # tmp = pd.pivot_table(tmp, index='trade_date', columns='fund_id', values='data_type').sort_index()
        sql_script = "SELECT * FROM {}.r_st_nav_attr_df where tjrq >= {} and tjrq <= {}".format(
                      db_name, self.start_date, self.end_date)
        attr_df = self.fetch_data_batch(user_name, sql_script)

        attr_df = attr_df[['tjrq', 'jjdm', 'attr_type', 'data_type', 'style_factor', 'data_value']].rename(
            columns={"tjrq": "trade_date", "jjdm": "fund_id"})
        attr_df = attr_df[(attr_df['data_type'] == 'exposure') & (attr_df['attr_type'] != 'style')]

        attr_df_style_allo = pd.pivot_table(attr_df[attr_df['attr_type'] == 'style_allo'],
                                            index='fund_id', columns='style_factor', values='data_value')
        attr_df_sector = pd.pivot_table(attr_df[attr_df['attr_type'] == 'sector'],
                                        index='fund_id', columns='style_factor', values='data_value')

        return attr_df_sector


if __name__ == '__main__':
    FundStyleLabelCalculator(start_date='20210320', end_date='20210629')