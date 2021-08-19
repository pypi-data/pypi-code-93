from dataclasses import dataclass
import pandas as pd


@dataclass
class dpd:
    # col names of dataframe
    col_fpdxp_amt: str #flexible fpd
    col_is_fpdx: str #flexible fpd

    col_fpd0p_amt: str = "user_fpd0_principal"
    col_fpd7p_amt: str = "user_fpd7_principal"
    col_fpd15p_amt: str = "user_fpd15_principal"
    col_fpd30p_amt: str = "user_fpd30_principal"
    col_user_principal: str = "user_principal"
    col_is_fpd0: str = "is_fpd0"
    col_is_fpd7: str = "is_fpd7"
    col_is_fpd15: str = "is_fpd15"
    col_is_fpd30: str = "is_fpd30"
    col_user_cnt: str = "userid"


    def dpd_basic(self, x):
        """
        Calculate fpd amount level and user level statistics from df
        expect to group by before applying the function
        example: df.groupby(['user_type']).apply(dpd_basic)
        """
        d = {}
        d['fpdxp_amt'] = (x[self.col_fpdxp_amt].sum()/x[self.col_user_principal].sum())*100
        d['fpd0p_amt'] = (x[self.col_fpd0p_amt].sum()/x[self.col_user_principal].sum())*100
        d['fpd7p_amt'] = (x[self.col_fpd7p_amt].sum()/x[self.col_user_principal].sum())*100
        d['fpd15p_amt'] = (x[self.col_fpd15p_amt].sum()/x[self.col_user_principal].sum())*100
        d['fpd30p_amt'] = (x[self.col_fpd30p_amt].sum()/x[self.col_user_principal].sum())*100 

        d['fpdxp_user'] = (x[self.col_is_fpdx].sum()/x[self.col_user_cnt].count())*100
        d['fpd0p_user'] = (x[self.col_is_fpd0].sum()/x[self.col_user_cnt].count())*100
        d['fpd7p_user'] = (x[self.col_is_fpd7].sum()/x[self.col_user_cnt].count())*100
        d['fpd15p_user'] = (x[self.col_is_fpd15].sum()/x[self.col_user_cnt].count())*100
        d['fpd30p_user'] = (x[self.col_is_fpd30].sum()/x[self.col_user_cnt].count())*100
        d['user_cnt'] = x[self.col_user_cnt].count()
        return pd.Series(d, index=['fpdxp_amt','fpd0p_amt', 'fpd7p_amt','fpd15p_amt','fpd30p_amt','fpdxp_user','fpd0p_user','fpd7p_user','fpd15p_user','fpd30p_user','user_cnt'])

    def dpd_checking(self, x):
        """
        Calculate fpd amount level and user level statistics from df
        expect to group by before applying the function
        example: df.groupby(['user_type']).apply(dpd_basic)
        """
        d = {}
        d['fpdxp_principal'] = x[self.col_fpdxp_amt].sum()
        d['fpd0p_principal'] = x[self.col_fpd0p_amt].sum()
        d['fpd7p_principal'] = x[self.col_fpd7p_amt].sum()
        d['fpd15p_principal'] = x[self.col_fpd15p_amt].sum()
        d['fpd30p_principal'] = x[self.col_fpd30p_amt].sum()

        d['fpdxp_user_cnt'] = x[self.col_is_fpdx].sum()
        d['fpd0p_user_cnt'] = x[self.col_is_fpd0].sum()
        d['fpd7p_user_cnt'] = x[self.col_is_fpd7].sum()
        d['fpd15p_user_cnt'] = x[self.col_is_fpd15].sum()
        d['fpd30p_user_cnt'] = x[self.col_is_fpd30].sum()
        d['user_cnt'] = x[self.col_user_cnt].count()
        d['user_principal'] = x[self.col_user_principal].sum()
        return pd.Series(d, index=['fpdxp_principal','fpd0p_principal', 'fpd7p_principal','fpd15p_principal','fpd30p_principal','fpdxp_user_cnt','fpd0p_user_cnt','fpd7p_user_cnt','fpd15p_user_cnt','fpd30p_user_cnt','user_cnt', 'user_principal'])


