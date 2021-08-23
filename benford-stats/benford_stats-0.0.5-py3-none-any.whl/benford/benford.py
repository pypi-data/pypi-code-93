import pandas as pd
import matplotlib.pyplot as plt
from math import log, log10, floor
from pandas.core import api
from scipy.stats import chi2
from numpy import random, quantile


def benford_table(n=4, transposed=False, percent=False, rounded=None):
    """Returns a dataframe which contains the probabilities from benfords law
    for the first n digits.
    """
    first_digit = [0] + [log10(1 + 1 / d) for d in range(1, 10)]
    nth_digit_list = []
    for _n in range(2, n + 1):
        digit_list = []
        for d in range(0, 10):
            digit_list.append(
                sum(
                    [
                        log10(1 + 1 / (10 * k + d))
                        for k in range(10 ** (_n - 2), 10 ** (_n - 1))
                    ]
                )
            )
        nth_digit_list.append(digit_list)
    nth_digit_list = [first_digit] + nth_digit_list

    df = pd.DataFrame(nth_digit_list, index=range(1, n + 1))

    if transposed:
        df = df.transpose()

    if percent:
        df *= 100

    if rounded:
        df = df.apply(round, args=[rounded])
    return df


def significant(num):
    """Calculates the significant of a given number"""
    return round(10 ** (log10(abs(num)) - floor(log10(abs(num)))), 10)


def nth_significant_digit(num, nth=1):
    """Return the nth significant digit."""
    return floor(significant(num) * 10 ** (nth - 1)) - 10 * floor(
        significant(num) * 10 ** (nth - 2)
    )


def frequency_table(sample, nth=1, percent=True):
    """Returns a Dataframe containing benfords probability for the nth digit
    and the empirical probability of the nth digit in the sample.
    """
    df = pd.DataFrame(sample)
    df = df[df[0] != 0]
    df["digit"] = df[0].apply(nth_significant_digit, args=[nth])
    digit_count = df.groupby("digit")["digit"].count()
    digit_count = digit_count / sum(digit_count) 

    digits = range(1, 10) if nth == 1 else range(0, 10)
    benford = benford_table(nth, percent=False, transposed=True)[nth]
    benford = benford[benford > 0].to_list()

    b = pd.DataFrame(zip(benford, digits), columns=["benford", "digit"]).set_index(
        "digit"
    )
    d = pd.DataFrame(digit_count).rename(columns={"digit": "sample_data"})
    table = b.merge(d, left_index=True, right_index=True, how="outer").fillna(0)

    if percent:
        table *= 100
    return table


# Visualisations:
def distribution_plot(
    table,
    title = "Vergleich der kumulierten Häufigkeiten", 
    sample_name = "sample-data"
    ):
    t = table.cumsum()
    fig, ax = plt.subplots()
    ax.step(x=t.index, y=t.sample_data, where="post", label=sample_name)
    ax.step(x=t.index, y=t.benford, where="post", label="benford")
    ax.set_ylabel("Kumulierte Häufigkeit", fontdict={"fontsize": 14})
    ax.set_title(title, fontdict={"fontsize": 22})
    ax.set_xlabel("Ziffer", fontdict={"fontsize": 14})
    ax.set_xticks(t.index)
    ax.set_xticklabels(t.index)
    ax.legend()
    ax.set_ylim([0, 105])
    fig.tight_layout()
    return fig


def barplot(
    table, 
    title = "Vergleich der Häufigkeiten in der Stichprobe zu Benfords Häufigkeiten", 
    sample_name = "sample-data"
    ):
    width = 0.35
    fig, ax = plt.subplots()
    rects1 = ax.bar(
        table.index - width / 2,
        round(table["sample_data"], 2),
        width,
        label=sample_name,
    )
    rects2 = ax.bar(
        table.index + width / 2, round(table["benford"], 2), width, label="benford"
    )
    ax.set_ylabel("Relative Häufigkeit in %", fontdict={"fontsize": 14})
    ax.set_title(
        title,
        fontdict={"fontsize": 22},
    )
    ax.set_xlabel("Ziffer", fontdict={"fontsize": 14})
    ax.set_xticks(table.index)
    ax.set_xticklabels(table.index)
    ax.legend()
    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    fig.tight_layout()
    return fig


def delta(table):
    return max(abs(table['sample_data'] - table['benford']))


def chi_squared_statistic(sample):
    df = pd.DataFrame(sample)
    df['digit'] = df[0].apply(nth_significant_digit)
    obs = df.groupby('digit')['digit'].count()
    obs = pd.DataFrame(range(1,10))\
            .set_index(0)\
            .merge(obs, right_index=True, left_index=True, how='outer')\
            .fillna(0)
    exp = [log10(1+1/d)*len(sample) for d in range(1,10)]
    return sum(abs(obs.digit-exp)**2/exp)


def chi_squared_critical(alpha=0.01, df=8):
    if alpha == 0.05 and df == 8:
        return 15.507
    if alpha == 0.01 and df ==8:
        return 20.090
    return chi2.ppf(q=1-alpha, df=df)


def chi_squared_passed(sample, alpha=0.01, df=8):
    """
    H0: Sample is Benford
    H1: Sample is not Benford
    We reject H0 if the test statistic is greater then the critical value.
    """
    return chi_squared_statistic(sample) <= chi_squared_critical(alpha=alpha, df=df)


def kolmogorov_smirnov_statistic(sample):
    table = frequency_table(sample=sample, percent=False)
    table = table.cumsum()
    return max(abs(table.sample_data - table.benford))


def kolmogorov_smirnov_critical(alpha=0.01):
    """ If alpha is in [0.01, 0.05, 0.1] return tabulated Values from Morrow 2014
    Otherwise use approximation (Miller 1956). 
    """
    if alpha == 0.01:
        return 1.420
    if alpha == 0.05:
        return 1.148
    if alpha == 0.1:
        return 1.012
    return (-0.5 * log(alpha/2))**0.5


def kolmogorov_smirnov_passed(sample, alpha=0.01):
    return kolmogorov_smirnov_critical(alpha) >= kolmogorov_smirnov_statistic(sample) * (len(sample))**0.5


def sum_invariance_table(sample, absolute = False):
    df = pd.DataFrame(sample)
    df = df[df[0] != 0]
    df['significant'] = df[0].apply(significant)
    df['digit'] = df[0].apply(nth_significant_digit)
    result = df.groupby('digit')['significant'].sum()
    if not absolute:
        result /= df.significant.sum()
    return result


def suminvariance_test(sample, alpha = 0.01):
    t = pd.DataFrame(
        zip(
            range(1,10), 
            [1/9 for i in range(10)], 
            sum_invariance_table(sample)
        ), 
        columns=['digit', 'benford', 'sample_data']
    )
    t.set_index('digit', inplace=True)
    stat = max(abs(t.sample_data - t.benford))
    crit = kolmogorov_smirnov_critical(alpha)
    #print(crit, stat* len(sample)**0.5, stat)
    return crit >= stat * len(sample)**0.5



def mad_statistic(sample):
    t = frequency_table(sample, percent=False)
    return sum(abs(t.sample_data - t.benford))/9


def mad_critical(alpha = 0.01, size = 1000):
    # simulated values for alpha = 0.1, 0.05, 0.005
    if size==1000:
        if alpha == 0.1:
            return 0.01028306
        if alpha == 0.05:
            return 0.01128174
        if alpha == 0.01:
            return 0.0124312
    
    xi_vals = []
    for i in range(1000):
        sample = random.default_rng().uniform(0,10,size)
        sample = 2**sample
        stat = mad_statistic(sample)
        xi_vals.append(stat)
    
    return quantile(a=xi_vals, q=[1-alpha])[0]


def mad_passed(sample, alpha = 0.01, critical=None):
    if critical:
        return mad_statistic(sample,alpha) < critical 
    return mad_statistic(sample=sample) < mad_critical(alpha, len(sample))


def mad2_statistic(sample):
    t = frequency_table(sample, percent=False)
    return sum(abs(t.sample_data - t.benford))*(len(sample)**0.5)


def mad2_critical(alpha = 0.01, size = 1000):
    # simulated values for alpha = 0.1, 0.05, 0.005
    if size==1000:
        if alpha == 0.1:
            return 2.91119254
        if alpha == 0.05:
            return 3.17398838
        if alpha == 0.01:
            return 3.69144414
    
    xi_vals = []
    for i in range(1000):
        sample = random.default_rng().uniform(0,10,size)
        sample = 2**sample
        stat = mad2_statistic(sample)
        xi_vals.append(stat)
    
    return quantile(a=xi_vals, q=[1-alpha])[0]


def mad2_passed(sample, alpha = 0.01, critical=None):
    if critical:
        return mad2_statistic(sample,alpha) < critical 
    return mad2_statistic(sample=sample) < mad2_critical(alpha=alpha, size = len(sample))