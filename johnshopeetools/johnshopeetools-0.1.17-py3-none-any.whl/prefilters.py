from dataclasses import dataclass
import pandas as pd
import ast


@dataclass
class prefilters:
    # col names of dataframe
    reason_codes: list
    col_user_cnt: str = "userid"
    col_reason_codes: str = "reason_codes"
    col_underwriting_decision: str = "underwriting_decision"
    reason_codes_len: int = 20


    def _hit(self, x, prefilter_code):
        """
        function to check if a reason code exists in the whole reason code string
        """
        if prefilter_code in x[self.col_reason_codes]:
            return True
        else:
            return False

    def _first_hit(self, x, prefilter_code):
        """
        function to check if a reason code exists in the first position of the reason code string
        """
        reason_codes = ast.literal_eval(x[self.col_reason_codes]) #convert string to list
        first_reason = reason_codes[0]

        if prefilter_code == first_reason:
            return True
        else:
            return False

    def _only_hit(self, x, prefilter_code):
        """
        function to check if a reason code is the only reaon code exist in the reason code string
        """

        reason_codes_str = []
        reason_codes_str.append(prefilter_code)
        for i in range(self.reason_codes_len-1):
            reason_codes_str.append('')

        if x[self.col_reason_codes] == str(reason_codes_str):
            return True
        else:
            return False

    def generate_hit_cols(self, df):
        for code in self.reason_codes:
            df[f'{code}_hit'] = df.apply(self._hit, prefilter_code=code, axis=1)

        for code in self.reason_codes:
            df[f'{code}_first_hit'] = df.apply(self._first_hit, prefilter_code=code, axis=1)

        for code in self.reason_codes:
            df[f'{code}_only_hit'] = df.apply(self._only_hit, prefilter_code=code, axis=1)

        return df

    def rejection_rate(self, x, prefilter_code):
        d= {}
        # rejection rate out of total activation users
        d[f'{prefilter_code}_only_hit_rate'] = x[f'{prefilter_code}_only_hit'].sum()/x[self.col_user_cnt].count()
        d[f'{prefilter_code}_hit_rate'] = x[f'{prefilter_code}_hit'].sum()/x[self.col_user_cnt].count()
        d[f'{prefilter_code}_first_hit_rate'] = x[f'{prefilter_code}_first_hit'].sum()/x[self.col_user_cnt].count()

        # count
        d[f'{prefilter_code}_only_hit_cnt'] = x[f'{prefilter_code}_only_hit'].sum()
        d[f'{prefilter_code}_hit_cnt'] = x[f'{prefilter_code}_hit'].sum()
        d[f'{prefilter_code}_first_hit_cnt'] = x[f'{prefilter_code}_first_hit'].sum()

        # rejection rate out of rejected users
        d[f'{prefilter_code}_only_hit_rate_of_reject'] = x[f'{prefilter_code}_only_hit'].sum()/x[x[self.col_underwriting_decision]=='Reject'][self.col_user_cnt].count()
        d[f'{prefilter_code}_hit_rate_of_reject'] = x[f'{prefilter_code}_hit'].sum()/x[x[self.col_underwriting_decision]=='Reject'][self.col_user_cnt].count()
        d[f'{prefilter_code}_first_hit_rate_of_reject'] = x[f'{prefilter_code}_first_hit'].sum()/x[x[self.col_underwriting_decision]=='Reject'][self.col_user_cnt].count()

        return pd.Series(d, index=[f'{prefilter_code}_only_hit_rate',f'{prefilter_code}_hit_rate',f'{prefilter_code}_first_hit_rate',
            f'{prefilter_code}_only_hit_cnt',f'{prefilter_code}_hit_cnt',f'{prefilter_code}_first_hit_cnt',
            f'{prefilter_code}_only_hit_rate_of_reject',f'{prefilter_code}_hit_rate_of_reject',f'{prefilter_code}_first_hit_rate_of_reject',
            ])

@dataclass
class prefilters_v2:
    reason_codes: list
    col_reason_codes: str = "reason_codes"
    col_reason_code_01: str = "reason_code_01"
    col_reason_code_02: str = "reason_code_02"
    col_user_cnt: str = "userid"
    col_underwriting_decision: str = "underwriting_decision"
    reason_codes_len: int = 20

    def _hit(self, x, prefilter_code):
        """
        function to check if a reason code exists in the whole reason code string
        """
        if prefilter_code in x[self.col_reason_codes]:
            return True
        else:
            return False

    def _first_hit(self, x, prefilter_code):
        """
        function to check if a reason code exists in the first position of the reason code string
        """

        if prefilter_code == x[self.col_reason_code_01]:
            return True
        else:
            return False

    def _only_hit(self, x, prefilter_code):
        """
        function to check if a reason code is the only reaon code exist in the reason code string
        """

        if prefilter_code == x[self.col_reason_code_01] and x[self.col_reason_code_02]=="":
            return True
        else:
            return False

    def _generate_split_col_names(self):
        """
        Generate column names to store the split reason code string
        """
        split_col_names = []
        for i in range(1,self.reason_codes_len+1):
            code = str(i).zfill(2)
            reason_code_name = f"reason_code_{code}"
            split_col_names.append(reason_code_name)

        return split_col_names


    def decompose_reason_codes(self, df):
        """
        If reason code is still in one col, decompose into multiple cols
        """
        split_col_names = self._generate_split_col_names()

        df[self.col_reason_codes] = df[self.col_reason_codes].apply(lambda x: ast.literal_eval(str(x))) #convert string list col to list col
        df[split_col_names] = pd.DataFrame(df[self.col_reason_codes].tolist(), index=df.index)
        return df 

    def generate_hit_cols(self, df):
        for code in self.reason_codes:
            df[f'{code}_hit'] = df.apply(self._hit, prefilter_code=code, axis=1)

        for code in self.reason_codes:
            df[f'{code}_first_hit'] = df.apply(self._first_hit, prefilter_code=code, axis=1)

        for code in self.reason_codes:
            df[f'{code}_only_hit'] = df.apply(self._only_hit, prefilter_code=code, axis=1)

        return df

    def rejection_rate(self, x, prefilter_code):
        d= {}
        # rejection rate out of total activation users
        d[f'{prefilter_code}_only_hit_rate'] = x[f'{prefilter_code}_only_hit'].sum()/x[self.col_user_cnt].count()
        d[f'{prefilter_code}_hit_rate'] = x[f'{prefilter_code}_hit'].sum()/x[self.col_user_cnt].count()
        d[f'{prefilter_code}_first_hit_rate'] = x[f'{prefilter_code}_first_hit'].sum()/x[self.col_user_cnt].count()

        # count
        d[f'{prefilter_code}_only_hit_cnt'] = x[f'{prefilter_code}_only_hit'].sum()
        d[f'{prefilter_code}_hit_cnt'] = x[f'{prefilter_code}_hit'].sum()
        d[f'{prefilter_code}_first_hit_cnt'] = x[f'{prefilter_code}_first_hit'].sum()

        # rejection rate out of rejected users
        d[f'{prefilter_code}_only_hit_rate_of_reject'] = x[f'{prefilter_code}_only_hit'].sum()/x[x[self.col_underwriting_decision]=='Reject'][self.col_user_cnt].count()
        d[f'{prefilter_code}_hit_rate_of_reject'] = x[f'{prefilter_code}_hit'].sum()/x[x[self.col_underwriting_decision]=='Reject'][self.col_user_cnt].count()
        d[f'{prefilter_code}_first_hit_rate_of_reject'] = x[f'{prefilter_code}_first_hit'].sum()/x[x[self.col_underwriting_decision]=='Reject'][self.col_user_cnt].count()

        return pd.Series(d, index=[f'{prefilter_code}_only_hit_rate',f'{prefilter_code}_hit_rate',f'{prefilter_code}_first_hit_rate',
            f'{prefilter_code}_only_hit_cnt',f'{prefilter_code}_hit_cnt',f'{prefilter_code}_first_hit_cnt',
            f'{prefilter_code}_only_hit_rate_of_reject',f'{prefilter_code}_hit_rate_of_reject',f'{prefilter_code}_first_hit_rate_of_reject',
            ])