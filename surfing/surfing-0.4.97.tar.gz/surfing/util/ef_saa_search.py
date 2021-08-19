import gzip
import json
import boto3
import pandas as pd
import numpy as np
from surfing.data.wrapper.mysql import DerivedDatabaseConnector
from surfing.data.api.derived import DerivedDataApi
from surfing.data.view.derived_models import AllocationDistribution
s3 = boto3.resource('s3')

def get_effective_frontier(bucket:str='effective-frontier-result',key:str='effective_frontier_bk_v0'):
    obj = s3.Object(bucket, key)
    body = obj.get()['Body'].read()
    data = gzip.decompress(body).decode('utf-8')
    data = json.loads(data)
    data = pd.DataFrame(data)
    return data

def upload_derived(df, table_name):
    print(table_name)
    df.to_sql(table_name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')

def build_allocation_distribution():
    bk_result = get_effective_frontier()
    annual_ret_max = bk_result.annual_ret.max()
    mdd_max = bk_result[bk_result.annual_ret == annual_ret_max].mdd.values[0]
    bk_result = bk_result[bk_result.mdd <= mdd_max]
    mdd_min = bk_result.mdd.min()
    bar = int((mdd_max - mdd_min) / 0.0025 )
    res = []
    mdd_steps = list(np.linspace(mdd_min, mdd_max, bar))
    for mdd_b in mdd_steps[:-1]:
        mdd_e = mdd_steps[mdd_steps.index(mdd_b) + 1]
        idx = bk_result[(bk_result.mdd >= mdd_b) & (bk_result.mdd <= mdd_e) ].annual_ret.idxmax()
        dic = bk_result.loc[idx].to_dict()
        dic['mdd_up_limit'] = mdd_e
        res.append(dic)
    df = pd.DataFrame(res)
    df['cash'] = 1 - df.csi500-df.gem-df.gold-df.hs300-df.mmf-df.national_debt-df.sp500rmb
    df['version'] = 1
    upload_derived(df, AllocationDistribution.__table__.name)

def get_saa_from_mdd(mdd:float=0.15):
    df = DerivedDataApi().get_allocation_distribution()
    df = df[df.mdd < mdd]
    if df.empty:
        return {}
    else:
        return df.sort_values('mdd', ascending=False).iloc[0].to_dict()

if __name__ == "__main__":
    # normal return 
    get_saa_from_mdd(mdd=0.20)

    # abnormal return 
    get_saa_from_mdd(mdd=0.01)