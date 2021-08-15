import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from scipy import stats


def set_stats(data, option, precision):
    """
    Args:
        data: 需要进行统计的 DataFrame
        option: 统计项 List
        precision: 数据精度 （小数点位数）
    Returns:
        统计结果 DataFrame
    """
    all_index = pd.DataFrame()  # 初始化统计结果为DataFrame
    stats_result = {}
    for col in data.columns:
        # print('col', col)
        if is_numeric_dtype(data[col]):
            stats_result['Name'] = col  # 列名
            stats_result['Total Count'] = len(data[col])  # N 合计
            stats_result['N'] = data[col].count()  # N 非缺失
            stats_result['N*'] = data[col].isna().sum()  # N 缺失
            stats_result['% N'] = stats_result['N'] / stats_result['Total Count']  # 非缺失值占比
            stats_result['% Missing'] = stats_result['N*'] / stats_result['Total Count']  # 缺失值占比
            stats_result['Unique'] = len(data[col].unique())  # 唯一值数量
            stats_result['CumN'] = len(data[col])  # N 合计
            stats_result['Sum'] = data[col].sum()  # 总和
            stats_result['Min'] = data[col].min()  # 最小值
            stats_result['25%'] = np.quantile(data[col], 0.25, interpolation='lower')  # Q1
            stats_result['Median'] = data[col].median()  # 中位数
            stats_result['75%'] = np.quantile(data[col], 0.75, interpolation='higher')  # Q3
            stats_result['Max'] = data[col].max()  # 最大值
            stats_result['Mean'] = data[col].mean()  # 均值
            stats_result['SE Mean'] = data[col].sem()  # 均值标准误 Standard deviation
            stats_result['Mean'] = stats.tmean(data[col])  # 截尾均值 ------[TO DO]待转换为内置函数导入
            stats_result['Std'] = data[col].std()  # 标准差
            stats_result['Var'] = data[col].var()  # 方差
            stats_result['CV'] = data[col].std() / data[col].mean()  # 变异系数 Coefficient of variation

            stats_result['Range'] = data[col].max() - data[col].min()  # 极差
            stats_result['QRange'] = stats_result['75%'] - stats_result['25%']  # 四分位间距 Interquartile range
            stats_result['Mode'] = data[col].mode()  # 众数
            stats_result['Sum of squares'] = data[col].apply(np.square).sum()  # 平方和 Sum of squares
            stats_result['Skew'] = data[col].skew()  # 偏度 Skewness
            stats_result['Kurt'] = data[col].kurt()  # 峰度 Kurtosis

            # 递方均差 MSSD
            a = data[col].values
            temp = pd.DataFrame(np.array([(a[i + 1] - a[i]) for i in range(a.size - 1)]))
            stats_result['MSSD'] = temp.apply(np.square).sum() / (2 * (len(a) - 1))

            print(stats_result)

            # 整合统计指标
            all_index = pd.concat([all_index, pd.DataFrame(stats_result,index=[0])],ignore_index=True)

        else:
            stats_result['Name'] = col  # 列名
            stats_result['Total Count'] = len(data[col])  # N 合计
            stats_result['N'] = data[col].count()  # N 非缺失
            stats_result['N*'] = data[col].isna().sum()  # N 缺失
            stats_result['% N'] = stats_result['N'] / stats_result['Total Count']  # 非缺失值占比
            stats_result['% Missing'] = stats_result['N*'] / stats_result['Total Count']  # 缺失值占比
            stats_result['Unique'] = len(data[col].unique())  # 唯一值数量

            stats_result['CumN'] = ''  # N 合计
            stats_result['Sum'] = ''  # 总和
            stats_result['Min'] = ''  # 最小值
            stats_result['25%'] = ''  # Q1
            stats_result['Median'] = ''  # 中位数
            stats_result['75%'] = ''  # Q3
            stats_result['Max'] = ''  # 最大值
            stats_result['Mean'] = ''  # 均值
            stats_result['SE Mean'] = ''  # 均值标准误 Standard deviation
            stats_result['Mean'] = ''  # 截尾均值 ------[TO DO]待转换为内置函数导入
            stats_result['Std'] = ''  # 标准差
            stats_result['Var'] = ''  # 方差
            stats_result['CV'] = ''  # 变异系数 Coefficient of variation

            stats_result['Range'] = ''  # 极差
            stats_result['QRange'] = ''  # 四分位间距 Interquartile range
            stats_result['Mode'] = ''  # 众数
            stats_result['Sum of squares'] = ''  # 平方和 Sum of squares
            stats_result['Skew'] = ''  # 偏度 Skewness
            stats_result['Kurt'] = ''  # 峰度 Kurtosis
            stats_result['MSSD'] = ''  # 递方均差 MSSD

            print(stats_result)
            # 整合统计指标

            all_index = pd.concat([all_index, pd.DataFrame(stats_result,index=[0])],ignore_index=True)

    result = all_index.loc[:, option]
    result=result.round(precision)  # 设置数据精度
    return result


if __name__ == '__main__':
    data = pd.read_csv("d:/demo/class.csv")
    items = ['Name', 'Total Count', 'N', 'N*', '% N', '% Missing', 'Unique', 'CumN',
             'Sum', 'Min', '25%', 'Median', '75%', 'Max', 'Mean', 'Std', 'Var', 'CV',
             'Range', 'QRange', 'Mode', 'Sum of squares', 'Skew', 'Kurt', 'MSSD',
             'SE Mean']
    result = set_stats(data, items, 4)
    print(result)
