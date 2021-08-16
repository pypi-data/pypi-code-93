import pandas as pd
import glob
from ...wrapper.mysql import RawDatabaseConnector

def hf_fund_info(f):
    #f = '/Users/huangkejia/Downloads/pics/'
    csv = '跟踪产品.xlsx'
    sheet = '产品列表'
    df = pd.read_excel(f+csv,sheet_name=sheet)
    df.columns = df.iloc[0, :]
    df.drop(df.index[0], inplace=True)
    cols = df.columns.tolist()
    col_dic = {c: c.replace('*','') for c in cols}
    df = df.rename(columns=col_dic)
    td = pd.to_datetime(df.成立日期)
    td = [i.date() for i in td ]
    df= df[['策略类型','产品简称','产品ID','成立日期','机构ID','机构简称','基金经理','来源','净值来源']]
    dic = {
        '策略类型':'stg_type',
        '产品简称':'desc_name',
        '产品ID':'fund_id',
        '成立日期':'begin_date',
        '机构ID':'agency_id',
        '机构简称':'agency_name',
        '基金经理':'manager_name',
        '来源':'source',
        '净值来源':'nav_source',
    }
    df = df.rename(columns=dic)
    df.to_sql('hf_fund_info', RawDatabaseConnector().get_engine(), index=False, if_exists='append')

def hf_fund_nav(f):
    #f = '/Users/huangkejia/Downloads/pics/'
    csv = '跟踪产品.xlsx'
    sheet = '基金净值'
    df = pd.read_excel(f+csv,sheet_name=sheet)
    df = df.set_index('datetime')
    df = pd.DataFrame(df.stack()).reset_index()
    df = df.rename(columns={'level_1':'fund_id',0:'nav'})
    df.to_sql('hf_fund_nav', RawDatabaseConnector().get_engine(), index=False, if_exists='append')

def hf_index_price(f):
    #f = '/Users/huangkejia/Downloads/pics/'
    file_list = glob.glob(f+'*.xlsx')
    ls = ['/Users/huangkejia/Downloads/pics/跟踪产品.xlsx','/Users/huangkejia/Downloads/pics/全产品净值列表.xlsx']
    csv_list = [i for i in file_list if i not in ls]
    dics = {   
        'stg_longonly':'融智-股票策略-主观多头指数',
        'stg_indexpow':'融智-股票策略-量化多头指数',
        'stg_neomark':'融智-相对价值-股票市场中性指',
        'stg_future':'融智-管理期货-管理期货复合指数',
        'stg_hedge':'融智-股票策略-股票多空指数',
        'stg_timdriven':'朝阳永续-事件驱动精选指数',
        'stg_macrohedge':'融智-宏观策略指数',
        'stg_highfreq':'融智-相对价值-套利指数',
        'stg_bond':'融智-固定收益-固收复合指数',
        'stg_fof':'融智-组合基金指数',
    }
    dics_revs = {v:k for k,v in dics.items()}
    index_result = []
    for csv_i in csv_list:
        df = pd.read_excel(csv_i)
        df.columns = df.iloc[2, :]
        df.drop(df.index[0:3], inplace=True)
        _cols = df.columns.tolist()
        df = df.drop(columns=[_cols[3]])
        name_dic = {'指数日期':'index_date','指数计算日期':'calcu_date',_cols[2]:'close'}
        df = df.rename(columns=name_dic)
        for name, code_i in dics_revs.items():
            if name in csv_i:
                code = code_i
                break
        df.loc[:,'index_id'] = code    
        index_result.append(df)
    df_i = '/Users/huangkejia/Downloads/pics/朝阳永续-事件驱动精选指数.xls'
    df = pd.read_excel(df_i)

    _dic = {
        '时间':'index_date',
        '事件驱动精选指数':'close',
    }
    df = df[list(_dic.keys())].replace('--',None).dropna().rename(columns=_dic)
    df.loc[:,'calcu_date'] = df.index_date
    df.loc[:,'index_id'] = 'stg_timdriven'
    index_result.append(df)
    df_result = pd.concat(index_result)
    num = df_result.close.tolist()
    num = [i if isinstance(i, float) else float(i.replace(',','')) for i in num]
    df_result.close = num
    df_result.to_sql('hf_index_price', RawDatabaseConnector().get_engine(), index=False, if_exists='append')