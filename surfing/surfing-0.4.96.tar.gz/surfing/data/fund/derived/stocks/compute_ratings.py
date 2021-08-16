import numpy as np


# 估值数据
PE_THRESHOLDS = [50, 10]
PB_THRESHOLDS = [8, 1]
DYR_THRESHOLDS = [0.01, 0.05]
PEG_THRESHOLDS = [0.04, 0.16]

# 财务数据
ROE评级阈值 = [0.05, 0.2]
ROIC评级阈值 = [0.03, 0.12]
ROA评级阈值 = [0.005, 0.1]
毛利润率阈值 = [0.05, 0.4]

经营现金流净值比利润总额阈值 = [0.4, 1.2]
所得税比利润总额阈值 = [0.2, 0.02]
营业外支出比利润总额阈值 = [0.005, 0.02]

自由现金流对净利润比评级阈值 = [0.5, 1.25]
资本支出比净利润阈值阈值 = [0.06, 0.03]

流动比率评级阈值 = [0.5, 2.0]
利息保障倍数评级阈值 = [1, 10]

近1年净利润增速阈值 = [0.04, 0.16]
自由现金流年成长率阈值 = [0.04, 0.16]

现金周转天数评级阈值 = [365, 0]


def rating_by_thresholds(df, name, thresholds):
    def rating(value):
        if np.isnan(value):
            return np.NaN

        if value < 0:
            return 1

        if len(thresholds) < 2:
            print('thresholds不能少于2个')

        ascending = thresholds[-1] > thresholds[0]
        if ascending:
            if value <= thresholds[0]:
                return 1
            if value >= thresholds[-1]:
                return 99
            return (value - thresholds[0]) / (thresholds[-1] - thresholds[0]) * 100
        else:
            if value >= thresholds[0]:
                return 1
            if value <= thresholds[-1]:
                return 99
            return (thresholds[0] - value) / (thresholds[0] - thresholds[-1]) * 100

    df[name + '评级'] = df[name].apply(rating)
    df[name + '评级'] = df[name + '评级'].fillna(0)

    return df


def compute_price_ratings(df):

    df = rating_by_thresholds(df, 'TTM.市盈率', PE_THRESHOLDS)
    df = rating_by_thresholds(df, '市净率', PB_THRESHOLDS)
    df = rating_by_thresholds(df, '股息率', DYR_THRESHOLDS)
    df = rating_by_thresholds(df, 'PEG', PEG_THRESHOLDS)
    df['估值评分'] = df['TTM.市盈率评级'] * 0.25 + df['市净率评级'] * 0.25 + df[
        '股息率评级'] * 0.25 + df['PEG评级'] * 0.25

    return df


def compute_finance_ratings(df):
    # 盈利能力
    df = rating_by_thresholds(df, 'TTM.平均ROE', ROE评级阈值)
    df = rating_by_thresholds(df, 'TTM.ROIC', ROIC评级阈值)
    df = rating_by_thresholds(df, 'TTM.ROA', ROA评级阈值)
    df = rating_by_thresholds(df, 'TTM.毛利润率', 毛利润率阈值)
    df['盈利能力评级'] = df['TTM.平均ROE评级'] * 0.25 + df['TTM.ROIC评级'] * 0.25 + df['TTM.ROA评级'] * 0.25 + df['TTM.毛利润率评级'] * 0.25
    # 收益质量
    df = rating_by_thresholds(df, 'TTM.经营现金流净值比利润总额', 经营现金流净值比利润总额阈值)
    df = rating_by_thresholds(df, 'TTM.所得税比利润总额', 所得税比利润总额阈值)
    df = rating_by_thresholds(df, 'TTM.营业外支出比利润总额', 营业外支出比利润总额阈值)
    df['收益质量评级'] = df['TTM.经营现金流净值比利润总额评级'] * 0.4 + df['TTM.所得税比利润总额评级'] * 0.3 + df['TTM.营业外支出比利润总额评级'] * 0.3

    # 现金流量
    df = rating_by_thresholds(df, 'TTM.自由现金流对净利润比', 自由现金流对净利润比评级阈值)
    df = rating_by_thresholds(df, 'TTM.资本支出比净利润', 资本支出比净利润阈值阈值)
    df['现金流量评级'] = df['TTM.自由现金流对净利润比评级'] * 0.6 + df['TTM.资本支出比净利润评级'] * 0.4

    # 运营效率
    df = rating_by_thresholds(df, '现金周转天数', 现金周转天数评级阈值)
    df['运营效率评级'] = df['现金周转天数评级']

    # 资本结构
    df = rating_by_thresholds(df, '流动比率', 流动比率评级阈值)
    df = rating_by_thresholds(df, '利息保障倍数', 利息保障倍数评级阈值)
    df['资本结构评级'] = df['流动比率评级'] * 0.5 + df['利息保障倍数评级'] * 0.5

    # 成长能力
    df = rating_by_thresholds(df, '单季度.自由现金流年成长率', 自由现金流年成长率阈值)
    df = rating_by_thresholds(df, '近1年净利润增速', 近1年净利润增速阈值)
    df['成长能力评级'] = df['单季度.自由现金流年成长率评级'] * 0.5 + df['近1年净利润增速评级'] * 0.5

    df['财务评分'] = df['盈利能力评级'] * 0.2 + df['收益质量评级'] * 0.2 + df[
        '现金流量评级'] * 0.2 + df['运营效率评级'] * 0.2 + df['资本结构评级'] * 0.2 + df['成长能力评级'] * 0.2

    return df

