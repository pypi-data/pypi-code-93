from dataclasses import dataclass
import pandas as pd
import ast


@dataclass
class util:
    # col names of dataframe
    col_is_fpd: str
    col_fpd_amt: str

    col_user_cnt: str = "userid"
    col_user_principal: str = "user_principal"

    col_total_credit_limit: str = "total_credit_limit"

    def fpdxp(self, x):
        d = {}
        d['user_cnt'] = x[self.col_user_cnt].count()
        d['fpdxp_user'] = (x[self.col_is_fpd].sum() /
                           x[self.col_user_cnt].count())*100
        d['fpdxp_amt'] = (x[self.col_fpd_amt].sum() /
                          x[self.col_user_principal].sum())*100

        d['fpdxp_cnt'] = x[self.col_user_cnt][x[self.col_is_fpd]
                                              == 1].count()  # cnt the no of users with dpd
        # sum the quota for dpd users
        d['is_fpdxp_limit_sum'] = x[self.col_total_credit_limit][x[self.col_is_fpd]].sum()
        # sum the principal for dpd users
        d['is_fpdxp_used_amt'] = x[self.col_user_principal][x[self.col_is_fpd]].sum()

        d['limit_sum'] = x[self.col_total_credit_limit].sum()
        d['used_amt'] = x[self.col_user_principal].sum()

        d['avg_limit'] = x[self.col_total_credit_limit].mean()

        return pd.Series(d, index=['user_cnt', 'fpdxp_user', 'fpdxp_amt', 'fpdxp_cnt',
                                   'is_fpdxp_limit_sum',
                                   'is_fpdxp_used_amt',
                                   'limit_sum',
                                   'used_amt',
                                   'avg_limit'])

    def limit_component(self, df, by):
        df_2 = df.groupby(by).apply(self.fpdxp)

        limit_bad = df_2['is_fpdxp_limit_sum']/df_2['fpdxp_cnt']
        limit_all = df_2['limit_sum']/df_2['user_cnt']
        limit_ratio = limit_bad/limit_all

        util_bad = df_2['is_fpdxp_used_amt']/df_2['is_fpdxp_limit_sum']
        util_all = df_2['used_amt']/df_2['limit_sum']
        util_ratio = util_bad/util_all

        validation = df_2['fpdxp_user'] * limit_ratio * util_ratio
        avg_limit = df_2['avg_limit']
        dpd_user = pd.DataFrame(df_2['fpdxp_user'])

        return limit_bad, limit_all, limit_ratio, util_bad, util_all, util_ratio, validation, avg_limit, dpd_user