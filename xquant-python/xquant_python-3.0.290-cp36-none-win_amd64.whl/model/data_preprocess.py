#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function
from builtins import (bytes, super, range, zip, round, pow, object)

from . import data_process_methods as dproc
import pandas as pd
try:
    import statsmodels.api as sm
except:
    raise Exception('please install statsmodels before use this submodel!')

MissingDataHandler = dproc.MissingDataHandler
PreCalHandler = dproc.PreCalHandler
Extreme_Data_Handler = dproc.Extreme_Data_Handler
NormDataHandler = dproc.NormDataHandler
FactorOrthHandler = dproc.FactorOrthHandler

"""
obtain data and preprocess
"""


def factors_preprocess(api, current_date, symbols = [], factors=[], pre_cal_types={}, miss_data_types={}, extreme_data_types={},
                       normalize_types={}, industry_field="SW1PLA.SET", other_infos={}):
    '''
    fucntion to obtain all preprocess factors
    :param api: sdk api
    :param current_date: current date
    :param factors: list of factor names
    :param pre_cal_types: pre-calculation method chosen by user for certain factors
    :param miss_data_types: missing data handle method chosen by user for certain factors
    :param extreme_data_types: extreme data handle method chosen by user for certain factors
    :param normalize_types: normalize data handle method chosen by user for certain factors
    :param industry_field:
    :param other_infos: other info may needed in this function (for extension purpose only)
    :return:
    '''
    if not symbols:
        symbols_raw = api.getSymbolPool()
    else:
        symbols_raw = symbols
    symbols = []
    for iSymbol in symbols_raw:
        if iSymbol.endswith('.CS'):
            symbols.append(iSymbol)

    industry_code = pd.Series(
        dproc.get_symbol_industry_map(api=api, symbols=symbols, industry_field=industry_field, date=current_date))

    # firstly, obtain raw dataframe for all factors
    preDate = api.getPrevTradeDate(current_date)
    rawData = api.getFieldsOneDay(symbols=symbols, fields=factors, tradeDate=preDate)
    rawData.index = rawData.symbol
    rawData["industry"] = pd.Series(industry_code)

    for factor in factors:
        # obtain user chosen methods
        i_cal_handler = PreCalHandler.get_method(pre_cal_types.get(factor, "null"))
        i_miss_data_handler = MissingDataHandler.get_method(miss_data_types.get(factor, "null"))
        i_extreme_data_handler = Extreme_Data_Handler.get_method(extreme_data_types.get(factor, "null"))
        i_normalize_handler = NormDataHandler.get_method(normalize_types.get(factor, "null"))
        i_other_info = other_infos.get(factor, None)

        rawData = single_factor_preprocess(data=rawData, factor_name=factor, pre_cal_handler=i_cal_handler, \
                                           miss_data_handler=i_miss_data_handler,
                                           extreme_data_handler=i_extreme_data_handler, \
                                           normalize_handler=i_normalize_handler, others=i_other_info)

    chooseColumns = factors + ["industry"]
    return rawData[chooseColumns]


# -------------------------------------------------------------------------------------------------------------------------------------------
def single_factor_preprocess(data, factor_name, pre_cal_handler=None, miss_data_handler=None, extreme_data_handler=None,
                             normalize_handler=None, others=None):
    '''
    function to process single factor, user may not use it
    :param data:
    :param factor_name:
    :param pre_cal_handler:
    :param miss_data_handler:
    :param extreme_data_handler:
    :param normalize_handler:
    :param others:
    :return:
    '''
    # handle missing data
    if miss_data_handler:
        data = miss_data_handler(df=data, factor_name=factor_name, others=others)
    # pre-process data
    if pre_cal_handler:
        data[factor_name] = data[factor_name].apply(pre_cal_handler)
    # handle extreme data
    if extreme_data_handler:
        data = extreme_data_handler(df=data, factor_name=factor_name, others=others)
    # handle normalization
    if normalize_handler:
        data = normalize_handler(df=data, factor_name=factor_name, others=others)
    return data


# -------------------------------------------------------------------------------------------------------------------------------------
"""
neutralize
"""


# ------------------------------------------------------------------------------------------------------------------------------------
def neutralize_factors(df, df_neutral, neutral_factors={}, industry_neutralize={}):
    '''
        neutralize Single Factor.
        :param df: df is the dataframe of target factors,the first column is "industry",others are factor names.
         :param df_neutral: dataframe of netural factors
        :param neutral_factors: dict of factor:[] to specify which factors to choose in the df_neutral for a certain factor, default is all
        :param industry_neutralize: True or False for certain factors,True is industry neutralize,False does not. default is True
        :return:
    '''

    if (df is None) or (df_neutral is None):
        return df

    # obtain column names
    neutralizedName = [factor for factor in df.columns.tolist() if factor != "industry"]
    allNeutralNames = [factor for factor in df_neutral.columns.tolist() if factor != "industry"]

    if "industry" not in df.columns.tolist():
        print("error! the industry not in df")
        return None
    else:
        factors = df[neutralizedName]
        industry_dummies = pd.get_dummies(df["industry"], prefix="IND")
        X = pd.concat([df_neutral[allNeutralNames], industry_dummies], axis=1)

    # obtain all netural factor names include industry code
    allNeutralColumnNames = X.columns.tolist()

    factorsNeutralied_df = pd.DataFrame(index=df.index, columns=neutralizedName)
    for iFactor in neutralizedName:
        Y = factors[iFactor]
        # get factor neutralize factors
        iNeturalFactors = neutral_factors.get(iFactor, allNeutralNames)
        # check if the factor need to add industry neturalize
        isIndustryNeutral = industry_neutralize.get(iFactor, True)

        chooseNames = []
        if iNeturalFactors and isIndustryNeutral:
            # obtain all neutral factor names, exclude factor names that are in allNeutralNames but not in iNeturalFactors
            excludeName = set(allNeutralNames) - set(iNeturalFactors)
            chooseNames = list(set(allNeutralColumnNames) - excludeName)
        elif iNeturalFactors:
            # use iNeturalFactors only
            chooseNames = iNeturalFactors
        elif isIndustryNeutral:
            # use industry only
            chooseNames = list(set(allNeutralColumnNames) - set(allNeutralNames))

        else:
            # use all
            chooseNames = allNeutralColumnNames
            pass

        # do calculation
        result_OLS = sm.regression.linear_model.OLS(Y, X[chooseNames], missing="drop").fit()
        factorsNeutralied_df[iFactor] = result_OLS.resid

    return factorsNeutralied_df
