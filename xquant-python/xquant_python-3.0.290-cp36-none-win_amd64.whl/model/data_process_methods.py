#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function
from builtins import (bytes, super, range, zip, round, pow, object)

import pandas as pd
import numpy as np

print_warning = False


class MissingDataHandler(object):
    """
    functions to handle missing data
    """
    method_map = {}

    @staticmethod
    def median(df, factor_name, others=None):
        '''
        function to fill missing data with median value
        :param df: dataframe for raw factor values
        :param factor_name: factor to work with, this is the name of the factor column
        :param others: other info may needed in this function (for extension purpose only)
        :return: the dataframe that the missing data is filled with median for a certain factor
        '''
        df[factor_name].fillna(df[factor_name].median(axis=0, skipna=True), inplace=True)
        return df

    @staticmethod
    def industry_median(df, factor_name, others=None):
        '''
        function to fill missing data with industry median value
        :param df: dataframe for raw factor values
        :param factor_name: factor to work with, this is the name of the factor column
        :param others: other info may needed in this function (for extension purpose only)
        :return: the dataframe that the missing data is filled with median for a certain factor
        '''
        dfTmp = df[[factor_name, "industry"]]
        dfTmp.index.name = "symbol"
        dfTmp_ = dfTmp.reset_index().set_index(["industry", "symbol"]).sort_index()
        dfTmp_ = dfTmp_.groupby(level=0).apply(lambda factor: factor.fillna(factor.median(axis=0, skipna=True)))
        dfTmp = dfTmp_.reset_index().set_index("symbol").sort_index()
        df[factor_name] = dfTmp[factor_name]
        return df

    @classmethod
    def set_usr_method(cls, name, function):
        cls.method_map[name] = function

    @classmethod
    def get_method(cls, name):
        i_method = cls.method_map.get(name, None)
        if i_method:
            return i_method
        else:
            if print_warning:
                print("[WARN]: MissingDataHandler method", name, "is not defined, will use default industry_median")
            return cls.method_map["industryMedian"]


# regiest pre-defined mathods
MissingDataHandler.method_map["median"] = MissingDataHandler.median
MissingDataHandler.method_map["industryMedian"] = MissingDataHandler.industry_median

# ---------------------------------------------------------------------------------------------------
'''class for handling pre-process of data by apply certain function to each factor value'''


# ---------------------------------------------------------------------------------------------------
class PreCalHandler(object):
    method_map = {
        "log": np.log,
        "null": None
    }

    @classmethod
    def set_usr_method(cls, name, function):
        cls.method_map[name] = function

    @classmethod
    def get_method(cls, name):
        i_method = cls.method_map.get(name, None)
        if i_method:
            return i_method
        else:
            if print_warning:
                print("[WARN]: PreCalHandler method", name, "is not defined, will use default null")
            return cls.method_map["null"]


# ---------------------------------------------------------------------------------------------------
'''class for handling extreme data'''


# ---------------------------------------------------------------------------------------------------
class Extreme_Data_Handler(object):
    """
    functions to handler extreme data
    """
    method_map = {}

    @staticmethod
    def mad(df, factor_name, others={"mad_number": 3}):
        '''
        funtion to fix extreme values for a factor, will replace them with median +- MAD value
        :param df: dataframe for factor values
        :param factor_name: factor to work with, this is the name of the factor column
        :param others: other info may needed in this function (for extension purpose only)
        :return: the dataframe that the extreme values are replaced with median +- MAD for a certain factor
        '''
        dfTmp = df[factor_name]
        # get median
        meadians = df[factor_name].median(axis=0, skipna=True)

        # get MAN num
        num = 3
        if others:
            num = others.get("mad_number", 3)

        # get MAD
        mad_value = num * 1.4826 * np.nanmedian(np.abs(df[factor_name].values - meadians))
        df[factor_name].clip(lower=meadians - mad_value, upper=meadians + mad_value, inplace=True)
        return df

    @classmethod
    def set_usr_method(cls, name, function):
        cls.method_map[name] = function

    @classmethod
    def get_method(cls, name):
        i_method = cls.method_map.get(name, None)
        if i_method:
            return i_method
        else:
            if print_warning:
                print("[WARN]: Extreme_Data_Handler method", name, "is not defined, will use default mad")
            return cls.method_map["mad"]


# regiest pre-defined mathods
Extreme_Data_Handler.method_map["mad"] = Extreme_Data_Handler.mad

# ---------------------------------------------------------------------------------------------------
'''class for handling normalization'''


# ----------------------------------------------------------------------------------------------------
class NormDataHandler(object):
    """
    functions to normalized data
    """
    method_map = {}

    @staticmethod
    def zscore(df, factor_name, others=None):
        '''
        normalize factor value by using z-score
        :param df: dataframe for factor values
        :param factor_name: factor to work with, this is the name of the factor column
        :param others: dict to save "zscoreWeights" if the weights for each symbol are not the same. The values are saved in dict,
        such as {"000001.CS":0.01, "000002.CS":0.02, ...}. The weights should be normalized before hands
        :return: the dataframe that the target factor is normalized by z-score method
        '''
        mean_weight = 0.
        if others is None:
            mean_weight = df[factor_name].mean(axis=0, skipna=True)
        else:
            if "zscoreWeights" in others.keys():
                weights = others["zscoreWeights"]
                # use the pre-calculated weight for the factor
                mean_weight = df[factor_name].mul(pd.Series(weights), axis=0).sum(axis=0, skipna=True)
        df[factor_name] = (df[factor_name].sub(mean_weight)) / df[factor_name].std(axis=0, skipna=True)
        return df

    @classmethod
    def set_usr_method(cls, name, function):
        cls.method_map[name] = function

    @classmethod
    def get_method(cls, name):
        i_method = cls.method_map.get(name, None)
        if i_method:
            return i_method
        else:
            if print_warning:
                print("[WARN]: NormDataHandler method", name, "is not defined, will use default zscore")
            return cls.method_map["zscore"]


# regiest pre-defined mathods
NormDataHandler.method_map["zscore"] = NormDataHandler.zscore

# ---------------------------------------------------------------------------------------------------
''' class for factor orthogonal'''


# ---------------------------------------------------------------------------------------------------

class FactorOrthHandler(object):
    """
    functions to orthogonal among factors
    """
    method_map = {}

    @staticmethod
    def symmetrical(df, factor_name, others=None):
        '''
        orthogonal among factors
        :param df: dataframe for factor values
        :param factor_name:factor to work with, this is the name of the factor column
        :param others:
        :return:  the dataframe that the target factor is orthogonalized
        '''

        dfTmp = df[factor_name]
        factor_arr = np.array(df[factor_name])
        factor_dot_arr = np.dot(factor_arr.T, factor_arr)
        U, V = np.linalg.eig(factor_dot_arr)
        one_arr = np.identity(len(dfTmp.columns))
        D = one_arr * U
        D_inv = np.linalg.inv(D)
        S = V.dot(np.sqrt(D_inv)).dot(V.T)
        dfTmp_ = dfTmp.dot(S)
        dfTmp_.columns = dfTmp.columns
        return dfTmp_

    @classmethod
    def set_usr_method(cls, name, function):
        cls.method_map[name] = function

    @classmethod
    def get_method(cls, name):
        i_method = cls.method_map.get(name, None)
        if i_method:
            return i_method
        else:
            if print_warning:
                print("[WARN]: FactorOrthHandler method", name,
                      "is not defined, will use default symmetrical")
            return cls.method_map["symmetrical"]


# regiest pre-defined mathods
FactorOrthHandler.method_map["symmetrical"] = FactorOrthHandler.symmetrical

# ---------------------------------------------------------------------------------------------------
'''help functions for factor neutralization'''
# ---------------------------------------------------------------------------------------------------
"""
function to obtain industry code for symbols
"""


def get_symbol_industry_map(api, symbols, industry_field, date):
    '''

    :param api:
    :param symbols:
    :param industry_field:
    :param date:
    :return:
    '''
    # get all industry code
    allIndustries = get_industry_codes(api, industry_field, date)
    # print("allIndustries", allIndustries)
    # loop over each industry code to get the ticker in each industry
    tickerIndustryMap = {}
    for iIndustry in allIndustries:
        # print(api.getRefData(iIndustry))
        iTickers = api.getConstituentSymbols(iIndustry, date)
        # print("iIndustry", iIndustry)
        # print("iIndustry tickers", iTickers)
        for symbol in iTickers:
            if symbol in symbols:
                tickerIndustryMap[symbol] = iIndustry
    return tickerIndustryMap


def get_industry_codes(api, industry_field, date):
    return api.getConstituentSymbols(industry_field, date)


def get_industry_symbols(api, industry_code, date):
    return api.getConstituentSymbols(industry_code, date)


def get_industry_exporsure(api, tickers, date, industry_code):
    # get tickerIndustry map
    tickerIndustryMap = get_symbol_industry_map(api, tickers, industry_code, date)
    # print(tickerIndustryMap)
    industry_codes = api.getConstituentSymbols(industry_code, date)
    df = pd.DataFrame(index=industry_codes, columns=tickers)
    for stk in tickers:
        try:
            df[stk][tickerIndustryMap[stk]] = 1
        except:
            continue
    return df.fillna(0)
