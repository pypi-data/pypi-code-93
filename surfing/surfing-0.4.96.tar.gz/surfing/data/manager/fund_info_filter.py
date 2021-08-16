from typing import List
import pandas as pd
import numpy as np
import json
import datetime

# 回测底层基金黑名单，筛掉没有办法处理的问题基金 2020-05-30
## #摘牌基金 发生大额申赎，导致净值剧烈波动， 用东财机构持有权重数据无法过滤
##'020035!0': 国泰上证5年期国债ETF联接A  '020036!0' 国泰上证5年期国债ETF联接C
BLACK_SHEEP = ['020035!0', '020036!0']

#基金基准发生改变  2020-06-22
##'320014!0':诺安沪深300指数增强   '050021!0':‘博时创业版ETF联接A 
BLACK_SHEEP.extend(['320014!0', '050021!0'])

#基金类别改变 2020-06-30
## ‘000512!0’: '国泰沪深300指数增强A'   曾用名 国泰结构转型
BLACK_SHEEP.extend(['000512!0'])

#基金类别改变 2020-07-14
## ‘001879!0’: '长城创业板指数增强A'   曾用名 长城创新动力灵活配置混合基金
BLACK_SHEEP.extend(['001879!0'])

#基金类别改变 2020-07-27
## ’519034!0' "海富通中证500增强" 曾用名 海富通中证低碳
BLACK_SHEEP.extend(['519034!0'])

# 发生净值突变的分级基金 属于放宽国债tag，加入信用债下的基金  2020-06-22
## 向上波动 '164210!1': 天弘同利分级, '164703!1': 汇添富互利分级 ,
## 向下波动 '000428!0' : 易方达聚盈分级
BLACK_SHEEP.extend(['164210!1','164703!1', '000428!0'])

# 没有办法筛选掉，早期终止 2020-06-30
## 000169!1 泰达宏利高票息A
## 000022!0 南方中债中期票据A
BLACK_SHEEP.extend(['000169!1','000022!0'])

# 基金类型改变 货币型 变债券型 2020-10-22 稳健策略净值波动
## 380010!0    中银理财30天a -> 中银聚享债券a
## 380011!0    中银理财30天b -> 中银聚享债券b
BLACK_SHEEP.extend(['380010!0','380011!0'])

EHR_PROBLEM_EKYWORDS = {
    'E': ['ETF', 'REITs', 'ESG', 'CES'],
    'H': ['H股', 'A-H50', '50AH', '中证AH'],
    'R': ['REITs'],
}

# 绝对收益基金关键字
ALPHA_FUND_KEY_WORD = ['对冲策略','阿尔法','绝对收益','对冲套利','量化收益']
ALPHA_PATTEN = '|'.join(ALPHA_FUND_KEY_WORD)

def filter_fund_info(fund_info: pd.DataFrame, index_list: List[str]) -> pd.DataFrame:
    # 去掉基金份额 E类 H类 R类
    # E类 指定代销机构对基金
    # H类 基金场内上市份额
    # R类 对特定投资群体进行发售，特定群体指基本养老保险基金，企业年金计划筹集的资金等
    ehr_funds = []
    # 这里itertuples会比iterrows快1个数量级
    for r in fund_info[['desc_name', 'fund_id']].itertuples():
        for type_word, problem_words in EHR_PROBLEM_EKYWORDS.items():
            i = r.desc_name
            for problem_i in problem_words:
                i = i.replace(problem_i, '')
            if type_word in i:
                ehr_funds.append(r.fund_id)

    no_mmf_index = set(index_list) - set(['mmf'])
    fund_info = fund_info[
        (
            fund_info.index_id.isin(no_mmf_index)
            # 只选非分级基金
            & ((fund_info.structure_type == 0))
            # 去掉etf基金
            & (fund_info.is_etf != 1)
            # 只选择人民币支付的基金
            & (fund_info.currency == 'CNY')
            # 只选择开放式基金，去掉封闭式基金
            & (fund_info.is_open == 1)
            # 去掉基金份额类型是 E H R
            & (~fund_info.fund_id.isin(ehr_funds))
            # 去掉超短债类型的基金，国债tag下 13只
            & (~fund_info.desc_name.str.contains('超短债'))
            # 去掉短期融资债 10只
            & (~fund_info.desc_name.str.contains('短融')) 
            # 去掉双债型债券  双债多含可转债 共41只
            & (~fund_info.desc_name.str.contains('双债'))
            # 去掉短期纯债型基金
            & (fund_info.wind_class_2 != '短期纯债型基金')
            # 货币基金总共1000多只，fund indicator 计算压力大，当前人工用2020年5月的货币基金规模取了前50只作为 货币基金池
            | (fund_info.is_selected_mmf == 1)# & (~fund_info.desc_name.str.contains('B')))TODO 回测对比
            # 增加绝对收益型基金 17只
            | (fund_info.desc_name.str.contains(ALPHA_PATTEN))
        )
        & (~fund_info.fund_id.isin(BLACK_SHEEP))
    ].copy()
    
    fund_info = fund_info[~(fund_info.wind_class_2 == '普通股票型基金')].copy()
    fund_info = fund_info[~(fund_info.wind_class_2 == '偏股混合型基金')].copy()

    return fund_info

def fund_info_update(fund_info: pd.DataFrame):
    #增加绝对收益 到货币型基金 38只
    mmf_exp_fund_list = fund_info[fund_info.desc_name.str.contains(ALPHA_PATTEN)].index.tolist()
    fund_info.loc[mmf_exp_fund_list,'index_id'] = 'mmf'
    
    #国债类扩容
    fund_info.loc[fund_info.national_debt_extension == 1, 'index_id'] = 'national_debt'
            
    #增加港股基金 基准1含有恒生 共69只
    hsi_fund = []
    for r in fund_info.itertuples():
        if (r.benchmark_1) and ('恒生' in r.benchmark_1):
            hsi_fund.append(r.fund_id)
    fund_info.loc[fund_info.fund_id.isin(hsi_fund), 'index_id_new'] = 'hsi'

    #增加混合债型一级基金 到国债下，共271 （混合一级含股票， 股灾时mdd会扩大，还是考虑排除）
    #hybrid_class_1_funds = fund_info[fund_info['wind_class_2'] == '混合债券型一级基金'].fund_id.to_list()
    #fund_info.loc[fund_info.fund_id.isin(hybrid_class_1_funds), 'index_id_new'] = 'national_debt'
    fund_info.loc[:,'index_id'] = fund_info['index_id_new']

    return fund_info

def active_fund_info(fund_info: pd.DataFrame, fund_benchmark: pd.DataFrame):
    #active_stock_fund_list = ['普通股票型基金', '偏股混合型基金', '增强指数型基金','灵活配置型基金', '平衡混合型基金']
    active_stock_fund_list = ['普通股票型基金', '偏股混合型基金'] # 只保留普通股票型基金 和 偏股股票型基金
    stock_index = ['csi500','hs300']
    gem_index_list = ['cnext_lowv_bc','cnext_mome_gr','cnext_r','gei','gem','gem_50'] #创业板相关基准
    
    # 过滤基金 参考fund_info
    # 去掉基金份额 E类 H类 R类
    # E类 指定代销机构对基金
    # H类 基金场内上市份额
    # R类 对特定投资群体进行发售，特定群体指基本养老保险基金，企业年金计划筹集的资金等
    ehr_funds = []
    # 这里itertuples会比iterrows快1个数量级
    for r in fund_info[['desc_name', 'fund_id']].itertuples():
        for type_word, problem_words in EHR_PROBLEM_EKYWORDS.items():
            i = r.desc_name
            for problem_i in problem_words:
                i = i.replace(problem_i, '')
            if type_word in i:
                ehr_funds.append(r.fund_id)
    
    fund_info = fund_info[
        (
            # 只选非分级基金
            ((fund_info.structure_type == 0))
            # 去掉etf基金
            & (fund_info.is_etf != 1)
            # 只选择人民币支付的基金
            & (fund_info.currency == 'CNY')
            # 只选择开放式基金，去掉封闭式基金
            & (fund_info.is_open == 1)
            # 去掉基金份额类型是 E H R
            & (~fund_info.fund_id.isin(ehr_funds))
        )]
    fund_info = fund_info.set_index('fund_id').drop(['benchmark'], axis=1)
    fund_benchmark = fund_benchmark.set_index('fund_id')
    fund_info = fund_info.join(fund_benchmark)[['desc_name','start_date','end_date','wind_class_1','wind_class_2','benchmark_s_raw']].copy()
    stock_fund = fund_info[fund_info['wind_class_2'].isin(active_stock_fund_list)]
    res = []
    for r in stock_fund.itertuples():
        i = r.benchmark_s_raw
        if isinstance(i, str):
            i = json.loads(i)
            _n = 1
            dic = {'fund_id':r.Index}
            for index_id, w in i.items():
                dic[f'fund_{_n}'] = index_id
                dic[f'weight_{_n}'] = w
                _n += 1
            res.append(dic)
        elif pd.isnull(i):
            res.append({})     
    _benchmark_info = pd.DataFrame(res).dropna(subset=['fund_id']).set_index('fund_id')
    stock_fund = stock_fund.join(_benchmark_info).copy()
    stock_fund = stock_fund.dropna(subset=['weight_1']).copy()
    res = []
    for r in stock_fund.itertuples():
        tag_wait_list = []
        if r.weight_1 >= 0.5:
            tag_wait_list.append(r.fund_1)
        if r.weight_2 >= 0.5:
            tag_wait_list.append(r.fund_2)
        tag_list = [_i for _i in tag_wait_list if _i in stock_index]
        if len(tag_list) > 0:
            tag = tag_list[0]
        else:
            gem_list = [_i for _i in tag_wait_list if _i in gem_index_list]
            if len(gem_list) > 0:
                tag = gem_list[0]
            else:
                tag = None
        res.append(tag)
    stock_fund['index_id'] = res
    _res = []
    for index_id in ['hs300','csi500','gem']:
        _df = stock_fund[(stock_fund['index_id'] == index_id)]
        _res.append(_df)
    active_fund_info = pd.concat(_res)[['desc_name','start_date','end_date','wind_class_1','wind_class_2','index_id','weight_1']].rename(columns={'weight_1':'weight'}).reset_index()
    
    ###
    #人工增加中证500 hs300 主动型， 基金基准人工扩容 TODO
    csi500 = ['000001!0',
                '000021!0',
                '004065!0',
                '004272!0',
                '004273!0',
                '005188!0',
                '005189!0',
                '005355!0',
                '005356!0',
                '005385!0',
                '040007!0',
                '070002!0',
                '110011!0',
                '257010!0',
                '550009!0']
    
    hs300 = ['000011!0', '000551!0', '000761!0', '090003!0']
    fund_info.loc[csi500, 'index_id'] = 'csi500'
    fund_info.loc[hs300, 'index_id'] = 'hs300' 
    csi500_df = fund_info.loc[csi500][['desc_name','start_date','end_date','wind_class_1','wind_class_2','index_id']].reset_index()
    hs300_df = fund_info.loc[hs300][['desc_name','start_date','end_date','wind_class_1','wind_class_2','index_id']].reset_index()
    active_fund_info = active_fund_info.append(csi500_df).append(hs300_df)
    ###

    # 只选择成立一年的
    _begin_date = datetime.datetime.today().date() - datetime.timedelta(days=365)
    active_fund_info = active_fund_info[active_fund_info['start_date'] < _begin_date]
    return active_fund_info

def get_conv_funds(fund_conv_stats, fund_info):
    conv_df = fund_conv_stats.pivot_table(index='datetime', values='conv_weights', columns='fund_id')
    conv_funds = conv_df.columns[conv_df.max() > 20].tolist()
    conv_funds = fund_info[(fund_info['fund_id'].isin(conv_funds)) 
              & (fund_info.structure_type == 0)].fund_id.tolist()
    return conv_funds