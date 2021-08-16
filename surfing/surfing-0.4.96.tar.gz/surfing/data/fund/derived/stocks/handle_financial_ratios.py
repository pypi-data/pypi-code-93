import pandas as pd
import numpy as np
from ....manager.data_tables import StockInfoDataTables
from .constants import ROE有效阈值


def cut_out_roe(data):
    if np.isnan(data):
        return np.nan

    if data < -ROE有效阈值:
        return -ROE有效阈值
    if data > ROE有效阈值:
        return ROE有效阈值

    return data


def average(key, quarter_shift=1):
    # 计算指标跟上一期的平均值 todo 这里因为财报不足4期，先用1期数据
    return (key + key.shift(quarter_shift).fillna(method='pad'))/2


def unify_all_data(sdt):
    # todo 借壳上市处理
    index = sdt.income_ttm.index

    income_ttm = sdt.income_ttm
    income_q = sdt.income_q.reindex(index)[[
        '单季度.营业总收入',
        '单季度.营业利润',
        '单季度.利润总额',
        '单季度.归属于母公司股东的净利润',
    ]]

    cash_flow_ttm = sdt.cash_flow_ttm.reindex(index)
    cash_flow_q = sdt.cash_flow_q.reindex(index)[[
        '单季度.经营活动产生的现金流量净额',
        '单季度.购建固定资产、无形资产和其他长期资产所支付的现金',
    ]]
    balance = sdt.balance.reindex(index)

    df = pd.concat([income_ttm, cash_flow_ttm, balance, income_q, cash_flow_q], axis=1)
    df['期初净资产'] = df['归属于母公司股东权益合计'].shift(1)
    return df


def compute_ttm_quarterly_ratios(sdt: StockInfoDataTables):
    df = unify_all_data(sdt)
    df = df.sort_index()
    df = df.fillna(0)

    # 盈利能力指标计算
    df['净资产'] = df['归属于母公司股东权益合计']
    df['TTM.期初ROE'] = df['TTM.归属于母公司股东的净利润'] / df['期初净资产']
    df['TTM.期末ROE'] = df['TTM.归属于母公司股东的净利润'] / df['净资产']
    df['平均净资产'] = (df['期初净资产'] + df['净资产']) / 2
    df['TTM.平均ROE'] = 2 * df['TTM.归属于母公司股东的净利润'] / (df['期初净资产'] + df['净资产'])

    df['TTM.期初ROE'] = df['TTM.期初ROE'].apply(cut_out_roe)
    df['TTM.期末ROE'] = df['TTM.期末ROE'].apply(cut_out_roe)
    df['TTM.平均ROE'] = df['TTM.平均ROE'].apply(cut_out_roe)

    df['平均总资产'] = average(df['资产总计'])
    df['TTM.ROA'] = df['TTM.归属于母公司股东的净利润'] / df['平均总资产']

    df['NOPAT'] = (df['TTM.营业利润'] + df['TTM.财务费用']) * (1 - df['TTM.所得税费用'] / df['TTM.利润总额'])
    df['无息流动负债'] = df['应付票据'] \
                   + df['应付账款'] \
                   + df['预收款项'] \
                   + df['应付职工薪酬'] \
                   + df['应交税费'] \
                   + df['其他应付款合计'] \
                   + df['一年内的递延收益'] \
                   + df['其他流动负债']

    df['无息非流动负债'] = df['长期应付款'] \
                    + df['专项应付款'] \
                    + df['预计非流动负债'] \
                    + df['递延收益'] \
                    + df['递延所得税负债'] \
                    + df['其他非流动负债']
    df['投资资本'] = df['资产总计'] - df['无息流动负债'] - df['商誉']
    df['税后净营业利润'] = df['NOPAT']
    df['TTM.ROIC'] = df['NOPAT'] / df['投资资本']

    df['TTM.计算毛利润营业收入'] = \
        df['TTM.营业收入'] \
        + df['TTM.利息收入'] \
        + df['TTM.已赚保费'] \
        + df['TTM.手续费及佣金收入'] \
        + df['TTM.营业总收入其他项目']
    df['TTM.计算营业成本'] = df['TTM.营业成本'] + \
                   df['TTM.利息支出'] + \
                   df['TTM.手续费及佣金支出'] + \
                   df['TTM.研发费用'] + \
                   df['TTM.退保金'] + \
                   df['TTM.赔付支出净额'] + \
                   df['TTM.提取保险合同准备金净额'] + \
                   df['TTM.保单红利支出'] + \
                   df['TTM.分保费用'] + \
                   df['TTM.其他业务成本']
    df['TTM.毛利润'] = df['TTM.计算毛利润营业收入'] - df['TTM.计算营业成本']
    df['TTM.毛利润率'] = df['TTM.毛利润'] / df['TTM.营业总收入']
    df['TTM.净利润率'] = df['TTM.归属于母公司股东的净利润'] / df['TTM.营业总收入']
    df['TTM.研发费用率'] = df['TTM.研发费用'] / df['TTM.营业总收入']

    # 现金流量
    df['TTM.自由现金流'] = df['TTM.经营活动产生的现金流量净额'] - df['TTM.购建固定资产、无形资产和其他长期资产所支付的现金']
    df['TTM.自由现金流对营业收入比'] = df['TTM.自由现金流'] / df['TTM.营业总收入']
    df['TTM.自由现金流对净利润比'] = df['TTM.自由现金流'] / df['TTM.归属于母公司股东的净利润']
    df['TTM.资本支出'] = df['TTM.投资所支付的现金'] + df['TTM.购建固定资产、无形资产和其他长期资产所支付的现金'] + \
                 df['TTM.取得子公司及其他营业单位支付的现金净额'] + df['TTM.支付的其他与投资活动有关的现金']
    df['TTM.资本支出比营业收入'] = df['TTM.资本支出'] / df['TTM.营业总收入']
    df['TTM.资本支出比净利润'] = df['TTM.资本支出'] / df['TTM.归属于母公司股东的净利润']
    df['TTM.经营现金流比资本支出'] = df['TTM.经营活动产生的现金流量净额'] / df['TTM.资本支出']
    # df['TTM.折旧摊销'] = df['TTM.固定资产和投资性房地产折旧'] + df['TTM.无形资产摊销'] + df['TTM.长期待摊费用摊销']
    # df['TTM.折旧摊销比经营现金流'] = df['TTM.折旧摊销'] / df['TTM.经营活动产生的现金流量净额']
    # df['TTM.资本支出比折旧摊销'] = df['TTM.资本支出'] / df['TTM.折旧摊销']

    # 收益质量
    df['TTM.经营现金流净值比利润总额'] = df['TTM.经营活动产生的现金流量净额'] / df['TTM.利润总额']
    df['TTM.所得税比利润总额'] = df['TTM.所得税费用'] / df['TTM.利润总额']
    df['TTM.营业外支出比利润总额'] = df['TTM.营业外支出'] / df['TTM.利润总额']

    # 运营效率
    df['总资产周转天数'] = (df['平均总资产'] / df['TTM.营业总收入']) * 365
    df['总资产周转次数'] = df['TTM.营业总收入'] / df['平均总资产']

    df['应收'] = df['应收票据'] + \
               df['应收账款'] + \
               df['应收保费'] + \
               df['应收分保账款'] + \
               df['应收分保合同准备金'] + \
               df['其他应收款合计'] + \
               df['应收出口退税'] + \
               df['应收补贴款'] + \
               df['内部应收款'] + \
               df['长期应收款'] - \
               df['预付款项']

    df['年均应收'] = average(df['应收'])
    df['应收账款周转次数'] = df['TTM.营业总收入'] / df['年均应收']
    df['应收账款周转天数'] = (df['年均应收'] / df['TTM.营业总收入']) * 365

    df['应付'] = df['应付票据'] + \
                df['应付账款'] + \
                df['应付手续费及佣金'] + \
                df['应付职工薪酬'] + \
                df['应交税费'] + \
                df['其他应付款合计'] + \
                df['内部应付款'] + \
                df['保险合同准备金'] + \
                df['长期应付款'] + \
                df['专项应付款'] + \
                df['长期应付职工薪酬'] - \
                df['预付款项']
    df['年均应付'] = average(df['应付'])
    df['应付账款周转次数'] = df['TTM.营业成本'] / df['年均应付']
    df['应付账款周转天数'] = (df['年均应付'] / df['TTM.营业成本']) * 365
    df['年均存货'] = average(df['存货'])
    df['存货周转次数'] = df['TTM.营业成本'] / df['年均存货']
    df['存货周转天数'] = (df['年均存货'] / df['TTM.营业成本']) * 365
    df['运营周转天数'] = df['应收账款周转天数'] + df['存货周转天数']
    df['现金周转天数'] = df['应收账款周转天数'] + \
                   df['存货周转天数'] - \
                   df['应付账款周转天数']

    # 资本结构
    df['流动比率'] = df['流动资产合计'] / df['流动负债合计']
    df['利息保障倍数'] = (df['TTM.利润总额'] + df['TTM.财务费用']) / df['TTM.财务费用']
    df['流动资产比总资产'] = average(df['流动资产合计']) / df['平均总资产']
    df['非流动资产比总资产'] = average(df['非流动资产合计']) / df['平均总资产']
    df['净营运资本'] = df['应收票据'] + df['应收账款'] + df['预付款项'] + df['其他应收款合计'] + df['存货'] - df['无息流动负债'] + df['长期股权投资'] + df[
        '投资性房地产']
    df['有形资本'] = df['净营运资本'] + df['固定资产'] + df['在建工程']
    df['投资资本'] = df['资产总计'] - df['无息流动负债'] - df['商誉']
    df['有型资产比总资产'] = average(df['有形资本']) / df['平均总资产']
    df['资产负债率'] = average(df['负债合计']) / df['平均总资产']
    df['有息负债'] = df['负债合计'] - df['无息流动负债'] - df['无息非流动负债']
    df['有息负债率'] = average(df['有息负债']) / df['平均总资产']

    # 成长能力
    df['单季度.自由现金流'] = df['单季度.经营活动产生的现金流量净额'] - df['单季度.购建固定资产、无形资产和其他长期资产所支付的现金']
    df['单季度.自由现金流年成长率'] = df['单季度.自由现金流'].pct_change(periods=4)
    df['近1年净利润增速'] = df['TTM.归属于母公司股东的净利润'].pct_change(periods=4)

    return df[[
        'TTM.期初ROE',
        'TTM.期末ROE',
        'TTM.平均ROE',
        'TTM.ROA',
        'TTM.ROIC',
        'TTM.毛利润率',
        'TTM.研发费用率',

        'TTM.自由现金流对净利润比',
        'TTM.资本支出比净利润',
        # 'TTM.折旧摊销比经营现金流',
        # 'TTM.资本支出比折旧摊销',

        'TTM.经营现金流净值比利润总额',
        'TTM.所得税比利润总额',
        'TTM.营业外支出比利润总额',

        '总资产周转天数',
        '总资产周转次数',
        '应收账款周转天数',
        '应收账款周转次数',
        '应付账款周转天数',
        '应付账款周转次数',
        '存货周转天数',
        '存货周转次数',
        '现金周转天数',

        '流动比率',
        '利息保障倍数',
        '流动资产比总资产',
        '有型资产比总资产',
        '资产负债率',
        '有息负债率',
        '单季度.自由现金流年成长率',
        '近1年净利润增速',

        # prices ratios 需要的列
        '平均净资产',
        '平均总资产',
        '税后净营业利润',
        '投资资本',
        'TTM.归属于母公司股东的净利润',
        '净资产',
        'TTM.经营活动产生的现金流量净额',
        'TTM.营业总收入',
        'TTM.毛利润',
    ]]
