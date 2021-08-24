from canalyst_candas.utils import (
    get_api_headers,
    Getter,
    LogFile,
    SCENARIO_URL,
    crawl_company_pages,
    create_drivers_dot,
    df_filter,
    dot_parse,
    filter_dataset,
    get_company_info_from_ticker,
    get_drivers_from_model,
    get_forecast_url,
    get_forecast_url_data,
    get_model_info,
    get_request,
    get_scenario_url_data,
    json_to_df,
    map_scenario_urls,
    read_json,
    save_guidance_csv,
    send_scenario,
    get_excel_model,  # used externally
)
import __main__
from pyvis.network import Network
from functools import reduce
import networkx as nx
import plotly.express as px
from statistics import stdev
import os.path
import time
import requests
import numpy as np
import datetime

# import modin.pandas as pd
import pandas as pd
import sys
import json
import re

from urllib.parse import quote_plus
from io import StringIO

import boto3
import os
import string
import urllib3
from os import path

from joblib import Parallel, delayed

import multiprocessing

num_cores = multiprocessing.cpu_count()

urllib3.disable_warnings()
from openpyxl import load_workbook, styles
from pathlib import Path

from canalyst_candas.configuration.config import Config
from canalyst_candas.settings import CONFIG


# helper class for on the fly function generation used in the ForecastFrame concept
# where we try to change one param across multiple tickers for re-fit in the
# scenario engine
class FuncMusic(object):
    def apply_function(self, value, modifier, argument):
        self.value = value
        self.modifier = modifier
        self.argument = argument
        method_name = "func_" + str(self.modifier)
        method = getattr(
            self,
            method_name,
            lambda: "Invalid function: use add, subtract, divide, or multiply",
        )
        return method()

    def func_add(self):
        return float(self.value) + float(self.argument)

    def func_divide(self):
        return float(self.value) / float(self.argument)

    def func_multiply(self):
        return float(self.value) * float(self.argument)

    def func_subtract(self):
        return float(self.value) - float(self.argument)


# WIP Class for parsing json revenue builds in graph structure (as opposed to tree)
class FormulaGraph:
    def __init__(
        self,
        file_name=None,
        ticker=None,
        auto_parse=True,
        force=False,  # determines if the file json file will be force pulled from s3
    ):

        # Raise an error if a ticker or file name is not entered
        if not ticker and not file_name:
            raise ValueError(
                "You must pass in a value for either the ticker "
                "argument or file_name argument"
            )
        elif ticker and file_name:
            raise ValueError(
                "Only pass in a value for ticker OR file_name, not both. "
                "If you pass a ticker, the data will be pulled from s3. "
                "If you pass a file_name, the data will be pulled from that json file."
            )

        # Set json_file instance var if a valid file was passed
        self.json_file = ""
        if os.path.isfile(file_name):
            self.json_file = file_name
        else:
            raise ValueError(
                f"The value you passed for file_name, {file_name}, is not a valid"
                "JSON file"
            )

        # set instance variables
        self.ticker = ticker
        self.auto = auto_parse
        self.force = force
        self.node_dict = self.read_json()  # dictionary of all nodes in the tree

        # instance variables to be set in parse_formula_graph()
        self.formula_strings = (
            {}
        )  # use dynamic programming/memoization to store the formula strings of each node in the tree
        self.drivers = {}  # drivers and their values
        self.labels = {}  # node: time_series_description

        # automatically create string representation and code expression (without custom drivers)
        if auto_parse:
            # create a string representation of the precedent formula and dictionary of drivers, and compile into code expression
            self.parse_formula_graph()

    # return the node dictionary from the json file
    def read_json(self):
        with open(self.json_file) as f:
            return json.load(f)["NodeDict"]

    def parse_formula_graph(self):
        # by default we will parse the first cell in the json
        cell = list(self.node_dict.values())[0]

        self.string_representation = self.calculate_formula_string(cell)

    # recursive method which calculates the formula string of the given cell/node
    def calculate_formula_string(
        self, cell: dict  # dictionary with info for the given cell
    ):

        # cells id's are in the formula mo_name|period, so replace the vertical line with an underscore
        # and the "-" in the period
        cell_id = cell["Id"].replace("|", "_").replace("-", "_")

        # base case: if the cell is a driver or has no precedents (bottom of tree)
        if cell["PrecedentIds"] == []:
            # add drivers to the dictionary of drivers, replace the value of non drivers with their values
            if cell["IsDriver"]:
                self.drivers[cell_id] = float(cell["Value"])
                self.labels[cell_id] = cell["TimeSeriesDescription"]

                to_return = cell_id
            else:
                v = cell["Value"]
                if v is None:
                    v = "0.0"
                to_return = v

            return f"({to_return})"

        # get formula of this cell
        if cell["Formula"]:
            formula = cell["Formula"].replace("=", "")
            formula = formula[0].replace("+", "") + formula[1:]

        # change ^ (exp in excel) to ** (exp in python)
        formula = formula.replace("^", "**")

        if len(cell["PrecedentIds"]) > 2:
            print("test")

        # recursive case: replace each cell in this cells formula with that cells formula
        for prec_cell_id in cell["PrecedentIds"]:

            prec_cell = self.node_dict[prec_cell_id]
            val_to_replace = prec_cell["SimpleAddress"]

            # if formula has not been memoized, calculate it
            if prec_cell_id not in self.formula_strings:
                self.formula_strings[prec_cell_id] = self.calculate_formula_string(
                    prec_cell
                )

            # Currently, each cell does not reference each of it's precedent cells, so:
            # In order to solve this I would have to loop through each cell id in formula_strings and
            # replace its simple address with its formula string, which would mean slower runtime here
            val_to_insert = self.formula_strings[prec_cell_id]

            # replace the cell address with its formula
            if val_to_replace in formula:
                # use re.sub with \bstr\b to only replace exactly that formula
                formula = re.sub(
                    r"\b" + val_to_replace + r"\b", f"({val_to_insert})", formula
                )

        return formula

    # evaluate the code derived from the string using the drivers default passed in values
    def evaluate_node(self, node_id=None, drivers=None):
        # default to using the normal drivers
        if type(drivers) != dict:
            drivers = self.drivers
        else:
            drivers = {
                **self.drivers,
                **drivers,
            }  # replace drivers with passed in values

        functions = {
            "SUM": lambda *nums: sum(nums),
            "AVERAGE": lambda *nums: sum(nums) / len(nums),
            "ROUND": lambda num, decimal_pts: round(num, decimal_pts),
            "EOMONTH": self.eomonth,
        }

        if node_id is None:
            return eval(self.string_representation, {}, {**drivers, **functions})
        else:
            return eval(self.formula_strings[node_id], {}, {**drivers, **functions})

    # mimics excel function needed for evaluating some formula strings
    def eomonth(self, date, num_months):

        # parsing the date string, only take the first part since all the dates seem to be 12:00:00 AM
        split_date = date.split()
        date = split_date[0]

        # print a message just incase there's a date that's not 12:00:00 AM
        if " ".join(split_date[1:]) != "12:00:00 AM":
            print(
                "time is not 12 am. this might cause an issue"
                " in the eomonth function in the FormulaTree class"
            )

        import calendar

        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month // 12
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.datetime(year, month, day)

        # create a datetime object out of the date parameter
        SECONDS_IN_A_DAY = 86400
        date = datetime.datetime.fromisoformat(date)

        # add months to the date and get the last date of the month the date is in
        date = add_months(date, num_months)
        date = datetime.datetime(
            (date.year + (date.month // 12)), (date.month + 1) % 12, 1
        ) - datetime.timedelta(days=1)

        # return the timestamp as a number of days as opposed to seconds
        date = datetime.datetime.timestamp(date) / SECONDS_IN_A_DAY
        return date


# helper class to read a formula json
class FormulaTree:

    # author Sebastian Fisher 6-30-2021
    # json created by Ian Paul 2021
    def __init__(
        self,
        config: Config = None,
        file_name=None,
        ticker=None,
        auto_parse=True,
        force=False,
    ):
        self.config = config or CONFIG
        self.s3_client = Getter(self.config)
        if not ticker and not file_name:
            raise ValueError(
                "You must pass in a value for either the ticker argument or file_name argument"
            )
        elif ticker and file_name:
            raise ValueError(
                "Only pass in a value for ticker OR file_name, not both. If you pass a ticker, the data will be pulled from s3. If you pass a file_name, the data will be pulled from that json file."
            )

        self.json_file = ""
        self.ticker = ticker
        if ticker:
            # get rid of country symbol from ticker
            ticker = ticker.split()[0]
            # file on s3
            from_filename = f"DATA/{ticker}/{ticker}_revenue.json"
            # location to download
            to_dir = os.path.join(self.config.default_dir, f"DATA/{ticker}")
            to_filename = os.path.join(to_dir, f"{ticker}_revenue.json")

            self.json_file = to_filename

            # if the file doesn't exist, attempt to pull from s3
            if not os.path.isfile(to_filename) or force:
                # Make directories to file if they don't exist
                os.makedirs(to_dir, exist_ok=True)
                self.s3_client.get_s3_file(to_filename, from_filename)

        else:
            if os.path.isfile(file_name):
                self.json_file = file_name
            else:
                raise ValueError(
                    "The value you passed for file_name,"
                    f" {file_name}, is not a valid JSON file."
                )

        self.auto = auto_parse

        # These will be set later on in parse_formula_tree
        self.string_representation = None
        self.drivers = None
        self.custom_drivers = None
        self.driver_labels = None
        self.formula_code = None
        self.betas = {}
        self.cell_formulas = {}

        # automatically create string representation and code expression (without custom drivers)
        if auto_parse:
            # create a string representation of the precedent formula and dictionary of drivers, and compile into code expression
            self.parse_formula_tree()

    # Find "beta" value for each driver and custom driver
    def find_betas(self):
        curr_rev = self.evaluate_node()
        self.betas = self.find_betas_helper(self.drivers, curr_rev)
        self.betas.update(self.find_betas_helper(self.custom_drivers, curr_rev))

    def find_betas_helper(self, drivers_dict, curr_rev):
        betas = {}
        for driver in drivers_dict:
            curr_val = drivers_dict[driver]
            new_rev = self.evaluate_node(drivers={driver: curr_val * 1.01})
            beta = (new_rev - curr_rev) / curr_rev
            betas[driver] = beta
        return betas

    # evaluate the code derived from the string using the drivers default passed in values
    def evaluate_node(self, time_series="MO_RIS_REV", drivers=None):
        # default to using the normal drivers
        if type(drivers) != dict:
            drivers = {**self.drivers, **self.custom_drivers}
        else:
            drivers = {
                **self.drivers,
                **self.custom_drivers,
                **drivers,
            }  # replace drivers with passed in values

        functions = {
            "SUM": lambda *nums: sum(nums),
            "AVERAGE": lambda *nums: sum(nums) / len(nums),
            "ROUND": lambda num, decimal_pts: round(num, decimal_pts),
            "EOMONTH": self.eomonth,
        }

        if time_series == "MO_RIS_REV":
            return eval(self.formula_code, {}, {**drivers, **functions})
        else:
            return eval(self.cell_formulas[time_series], {}, {**drivers, **functions})

    # defining needed excel function
    def eomonth(date, num_months):

        # parsing the date string, only take the first part since all the dates seem to be 12:00:00 AM
        split_date = date.split()
        date = split_date[0]

        # print a message just incase there's a date that's not 12:00:00 AM
        if " ".join(split_date[1:]) != "12:00:00 AM":
            print(
                "time is not 12 am. this might cause an issue"
                " in the eomonth function in the FormulaTree class"
            )

        import calendar

        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month // 12
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.datetime(year, month, day)

        # create a datetime object out of the date parameter
        SECONDS_IN_A_DAY = 86400
        date = datetime.datetime.fromisoformat(date)

        # add months to the date and get the last date of the month the date is in
        date = add_months(date, num_months)
        date = datetime.datetime(
            (date.year + (date.month // 12)), (date.month + 1) % 12, 1
        ) - datetime.timedelta(days=1)

        # return the timestamp as a number of days as opposed to seconds
        date = datetime.datetime.timestamp(date) / SECONDS_IN_A_DAY
        return date

    # Creates a string representation of the formula tree
    def parse_formula_tree(self, custom_drivers_list=[]):

        # load the file from json
        with open(self.json_file) as f:
            cell_data = json.load(f)

        # Set up a dictionary for the values and labels of each driver variable
        drivers = {}
        labels = {}

        # Set up a dictionary for formula for each node in the tree
        self.cell_formulas = {}

        # start out with each custom driver as None value
        custom_drivers_list = list(custom_drivers_list)
        custom_drivers = dict((driver, None) for driver in custom_drivers_list)

        # call function to recur to precedent cells
        formula = self.create_cell_string_representation(
            cell_data, drivers, labels, custom_drivers
        )

        # set values of instance variables
        self.string_representation = formula
        self.drivers = drivers
        self.custom_drivers = custom_drivers
        self.driver_labels = labels

        # compile string representation into code expression
        self.formula_code = compile(
            ")\n".join(self.string_representation.split(")")), "<string>", "eval"
        )

        # calc betas
        self.find_betas()

    # creates a string representation of the formula for a given cell json
    def create_cell_string_representation(
        self, cell_data, drivers, labels, custom_drivers
    ):

        # get the formula and no_name of the cell from its json
        if cell_data["Formula"]:
            formula = cell_data["Formula"].replace("=", "")
            formula = formula[0].replace("+", "") + formula[1:]

        cell_mo_name = cell_data["RelationalCellAddress"]
        cell_mo_name = cell_mo_name[1 : cell_mo_name.find("|")]

        # Base case: if the cell is a driver, custom driver, or if it is historical,
        # then return that cells value or variable
        if (
            cell_data["PrecedentCellsCount"] == 0
            or cell_data["IsHistorical"]
            or cell_mo_name in custom_drivers
        ):

            # for drivers, add them to the right dictionary and return the mo name
            if cell_data["IsDriver"]:
                drivers[cell_mo_name] = float(cell_data["Value"])

                labels[cell_mo_name] = cell_data["TimeSeriesDescription"]
                to_return = cell_mo_name

            # do the same for custom drivers but with the custom drivers dict
            elif cell_mo_name in custom_drivers:
                custom_drivers[cell_mo_name] = float(cell_data["Value"])

                labels[cell_mo_name] = float(cell_data["Value"])
                to_return = cell_mo_name

            # Otherwise return the value of the cell
            else:
                v = cell_data["Value"]
                if v is None:
                    v = "0.0"
                to_return = v

            # making sure date values are adding with quotations around them
            if cell_data["Formula"] and "EOMONTH" in cell_data["Formula"]:
                return f'("{to_return}")'
            return f"({to_return})"

        # Recursive case: loop through the precedent cells of this cell, and replace
        # the formula with the string formulas of those cells
        for prec_cell_data in cell_data["PrecedentCells"]:
            # set the value to replace (the precedent cell's address)
            val_to_replace = prec_cell_data["SimpleAddress"]
            prec_cell_mo_name = prec_cell_data["RelationalCellAddress"]
            prec_cell_mo_name = prec_cell_mo_name[1 : prec_cell_mo_name.find("|")]

            # set the value to insert into the formula (the precedent cell's formula)
            if prec_cell_mo_name not in self.cell_formulas:
                val_to_insert = self.create_cell_string_representation(
                    prec_cell_data, drivers, labels, custom_drivers
                )
                self.cell_formulas[prec_cell_mo_name] = val_to_insert

            else:
                val_to_insert = self.cell_formulas[prec_cell_mo_name]

            # change ^ (exp in excel) to ** (exp in python)
            formula = formula.replace("^", "**")

            # replace the cell address with its formula
            if val_to_replace in formula:
                # formula = formula.replace(val_to_replace, f"({val_to_insert})")
                # use re.sub with \bstr\b to only replace exactly that formula
                formula = re.sub(
                    r"\b" + val_to_replace + r"\b", f"({val_to_insert})", formula
                )

        return formula


# a class of multiple models
class ModelSet:
    def __init__(
        self,
        ticker_list,
        config: Config = None,
        feature_list="",
        period_name="Q",
        allow_null=False,
        extract_drivers=True,
        historical_only=False,
    ):
        self.config = config or CONFIG
        self.historical_only = historical_only
        self.period_name = period_name
        self.extract_drivers = extract_drivers
        self.ticker = ticker_list
        self.ticker_list = ticker_list
        self.Drivers = None
        self.Models = {}
        self.log = LogFile(default_dir=self.config.default_dir)
        self.api_headers = get_api_headers(self.config.canalyst_api_key)

        self.get_featurelibrary()  # set self._features

        if type(ticker_list) is str:
            ticker_list = [ticker_list]

    # shows a tree for the given ticker and time series
    def show_tree(self, ticker, time_series="MO_RIS_REV", tree=True, notebook=True):
        model = self.Models[ticker]

        return model.show_tree(
            time_series=time_series,
            tree=tree,
            notebook=notebook,
            common_time_series=self._common_time_series_names,
        )

    # get a list of time series from the default dataframe
    def get_featurelist(self):
        df = self._features
        df = (
            df.groupby(["time_series_name"])
            .first()
            .reset_index()[["time_series_description", "time_series_name"]]
        )
        self.FeatureList = df
        return

    # search the time series for the default dataframe
    def time_series_search(self, search_term=""):
        df = self._features
        if search_term != "":
            df1 = df[
                df["time_series_description"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df2 = df[
                df["time_series_name"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df = pd.concat([df1, df2])
            df = (
                df.groupby(
                    ["time_series_name", "time_series_description", "category_slug"]
                )
                .first()
                .reset_index()
            )
        return df  # [['time_series_name','time_series_description','category_slug']]

    # search model drivers
    def driver_search(self, search_term="", col="time_series_name"):
        df = self.drivers
        if search_term != "":
            df1 = df[
                df["time_series_description"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df2 = df[
                df["time_series_name"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df = pd.concat([df1, df2])
            df = (
                df.groupby(
                    ["time_series_name", "time_series_description", "category_slug"]
                )
                .first()
                .reset_index()
            )
        return df  # [['time_series_name','time_series_description','category_slug']]

    # creates the default dataframes features and Drivers
    def get_featurelibrary(self, col="time_series_name"):
        if type(self.ticker_list) is list:

            list_all = []
            list_df = []
            for ticker in self.ticker_list:

                list_rows = []

                md = Model(config=self.config, ticker=ticker)
                self.Models[ticker] = md

                df = md._model_frame

                list_df.append(df)
                if df is not None:
                    list_rows = list(set(list(df[col])))
                    list_all.append(list_rows)

            df = pd.concat(list_df)
            # df = df.sort_values(["period_name", "name_index"])

            res = list(reduce(lambda i, j: i & j, (set(x) for x in list_all)))
            self._common_time_series_names = res

            df = df_filter(df, "time_series_name", res)

            self._features = df

            if self.extract_drivers == True:
                self.Drivers = df[df["is_driver"] == 1]
            return

        else:

            df = Model(
                config=self.config,
                ticker_list=self.ticker_list,
                extract_drivers=self.extract_drivers,
                historical_only=self.historical_only,
            ).model_frame()
            self._features = df
            if self.extract_drivers == True:
                self.Drivers = df[df["is_driver"] == 1]
            return
        return

    # allows for filtering and shaping the default dataframe
    # MODEL model_frame
    def model_frame(
        self,
        time_series_name="",
        period_name="",
        is_driver="",
        pivot=False,
        mrq=False,
        period_duration_type="",
        is_historical="",
        n_periods="",
        mrq_notation=True,
        warning=True,
    ):

        return filter_dataset(
            self._features,  # this is the core dataset of the modelset class
            time_series_name,
            period_name,
            is_driver,
            pivot,
            mrq,
            period_duration_type,
            is_historical,
            n_periods,
            mrq_notation,
            warning,
        )

    def modify_features(
        self, params, modifier, argument, period_name=""
    ):  # modifier = add,subtract,multiply,divide.  argument is the number to apply.
        if type(params) is not dict:
            print("Params must be a dictionary")
            return
        print("get drivers from model")

        dict_out = {}
        for count, ticker in enumerate(self.ticker_list):

            df = self.Models[ticker].default_df.head(1)

            df_filter = self.Models[ticker].default_df[
                self.Models[ticker].default_df["time_series_name"] == params[ticker]
            ]

            period_name = df_filter["period_name"].iloc[0]
            try:
                old_value = df_filter["value"].iloc[
                    0
                ]  # df_filter[df_filter['period_name']==period_name]['value'][0]
            except:
                self.log.write("modify features old_value_error")
                continue
            try:
                d = FuncMusic()
                new_value = d.apply_function(old_value, modifier, argument)

            except:
                self.log.write("modify features new_value_error")
                return df_filter

            dict_out[ticker] = [params[ticker], old_value, new_value, period_name]
        df = pd.DataFrame(dict_out).T.reset_index()
        df.columns = [
            "ticker",
            "time_series_name",
            "default_value",
            "scenario_value",
            "period_name",
        ]
        return df

    def forecast_frame(
        self, time_series_name, n_periods, function_name="value", function_value=""
    ):
        df = self.model_frame(
            [time_series_name],
            period_duration_type="fiscal_quarter",
            is_historical=False,
            n_periods=n_periods,
        )

        if function_name != "value":
            d = FuncMusic()
            df["new_value"] = df.apply(
                lambda row: d.apply_function(
                    row["value"], modifier=function_name, argument=function_value
                ),
                axis=1,
            )
        else:
            df["new_value"] = function_value

        df = df[
            [
                "ticker",
                "period_name",
                "time_series_name",
                "value",
                "new_value",
                "period_end_date",
            ]
        ]

        return df

    def fit(self, params, return_series):
        # ticker period time_series_name value new_value
        dict_summary = {}
        if type(params) is dict:
            df = pd.DataFrame.from_dict(params, orient="index").reset_index()
        else:
            df = params

        df_grouped = df.groupby(["ticker"]).first().reset_index()

        dict_data = {}
        for i, row in df_grouped.iterrows():

            df_ticker = df[df["ticker"] == row["ticker"]]
            ticker = row["ticker"]  # .iloc[0]
            self.Models[ticker].set_new_uuid()
            list_changes = []

            for i, row in df_ticker.iterrows():
                feature_value = row["new_value"]
                feature_name = row["time_series_name"]
                feature_period = row["period_name"]
                ticker = row["ticker"]

                list_changes.append(
                    {
                        "time_series": feature_name,
                        "period": feature_period,
                        "value_expression": {"type": "literal", "value": feature_value},
                    }
                )

                data = {"changes": list_changes, "name": self.Models[ticker].uuid}
                dict_data[ticker] = data

        res = Parallel(n_jobs=num_cores)(
            delayed(send_scenario)(
                ticker,
                data,
                self.api_headers,
                self.Models[ticker].csin,
                self.Models[ticker].latest_version,
                self.config.mds_host,
            )
            for ticker, data in dict_data.items()
        )

        ticker_list = list(set(list(df["ticker"])))

        for ticker in ticker_list:
            self.Models[ticker].model_fit(return_series)
            try:
                dict_summary[ticker] = self.Models[ticker].summary()
            except:
                self.log.write("Missing scenario for " + ticker)

        return dict_summary

    def filter_summary(self, dict_summary, period_type="Q"):

        pd.set_option("mode.chained_assignment", None)
        pd.set_option("display.float_format", lambda x: "%.5f" % x)

        list_out = []
        for ticker in dict_summary.keys():

            df = dict_summary[ticker]
            # df = df[df['time_series_name'].isin(time_series)]
            list_out.append(df)
        df = pd.concat(list_out)
        df["sort_period_name"] = (
            df["period_name"].str.split("-").str[1]
            + df["period_name"].str.split("-").str[0]
        )
        df = df.sort_values(["ticker", "sort_period_name"])
        df = df[df["period_name"].str.contains(period_type)]
        df = df.drop(columns="sort_period_name")

        return df


class ModelMap:
    def __init__(
        self,
        config: Config = None,
        ticker=None,
        model=None,
        time_series="MO_RIS_REV",
        col_for_labels="time_series_name",
        tree=True,
        common_size_tree=True,
        notebook=True,
        auto_download=True,
        tree_complexity_limit=None,  # model map will not display as a tree if its complexity is above this limit
        common_time_series=None,  # optional list of common features. nodes with this feature will be made triangles
    ):
        self.config = config or CONFIG
        self.s3_client = Getter(config=self.config)
        self.api_headers = get_api_headers(self.config.canalyst_api_key)

        if model:
            self.model = model
            self.ticker = self.model.ticker
        elif ticker:
            self.ticker = ticker
            self.model = None
        else:
            raise TypeError("You must pass in either a ticker or model")

        self.time_series = time_series
        self.col_for_labels = col_for_labels
        self.tree = tree
        self.common_size_tree = common_size_tree
        self.notebook = notebook
        self.auto_download = auto_download
        self.tree_complexity_limit = tree_complexity_limit
        if common_time_series:
            self.common_time_series = set(common_time_series)
        else:
            self.common_time_series = common_time_series

        # will be defined when create_model is called
        self.dot_file = None
        self.nodes = None
        self.path_distances = None
        self.complexity = None
        self.mean_end_node_distance = 0
        self.max_end_node_distance = 0
        self.std_dev_node_distance = 0

        # Create dataframe for precedent/dependent tree, graph of the tree, and a network of that graph (for visualization)
        self.df = self.load_data()
        self.network = self.create_model()

        self.fig = None

    # helper function to load data from candas:
    # loads model_frame for chosen ticker and create a dot file
    def load_data(self) -> pd.DataFrame:
        if self.model:
            cdm = self.model
        else:
            cdm = Model(config=self.config, ticker=self.ticker)

        df = cdm.model_frame(period_duration_type="fiscal_quarter", n_periods="")

        self.dot_file = create_drivers_dot(
            self.time_series, self.api_headers, self.ticker, self.config, self.s3_client
        )

        return df

    # create a model of the dot file and optionally download in an html file
    def create_model(self, toggle_drag_nodes=True):
        # read dot file into a graph
        G = nx.drawing.nx_pydot.read_dot(self.dot_file)

        # Create Network from nx graph and turn off physics so dragging is easier
        graph = Network(
            "100%",
            "100%",
            notebook=self.notebook,  # enables displaying in a notebook
            directed=True,  # makes edges arrows
            layout=self.tree,  # Creates tree structure
            bgcolor="#FFFFFF",
        )
        graph.toggle_physics(True)
        graph.from_nx(G)

        # update the complexity of the graph, and if it is greater than the limit, set self.Tree to False
        # won't do anything if tree_complexity_limit wasn't set
        self.complexity = len(graph.nodes)
        if self.tree_complexity_limit and self.complexity > self.tree_complexity_limit:
            self.tree = False

        # model_frame filtered with only needed time_series
        time_series = {}
        for node in graph.nodes:
            id_split = node["id"].split("|")
            if len(id_split) > 1:
                time_series[id_split[0]] = id_split[1]
        df = self.df[self.df["time_series_slug"].isin(time_series)]

        # root node id
        root_id = graph.nodes[0]["id"]

        # column to use for labels
        col_for_labels = self.col_for_labels

        # reformat nodes
        # path lengths between each node
        self.path_distances = dict(nx.all_pairs_shortest_path_length(G))
        num_drivers = 0
        distances = []
        for node in graph.nodes:

            # set level of node based on distance from root
            node["level"] = self.path_distances[root_id][node["id"]]

            # parse node id into time series slug and period name
            # AND get row with the given period and time series slug in dataframe
            id_split = node["id"].split("|")

            ###### SOLVE FOR MODELS CONTAINING MO.Lastprice (which is not in candas dataframe)
            # account for time series without a period (last price)
            if len(id_split) < 2:
                node["title"] = node["label"]
                continue
            ######

            slug = id_split[0]
            period = id_split[1]
            rows = df[df["period_name"] == period]

            row = rows[rows["time_series_slug"] == slug].iloc[0]

            # format colors of nodes and update data
            if row["is_driver"]:
                color = "rgba(200, 0, 0, 0.75)"

                ########## STATS #############
                # get dist from root node, add to mean and find new max
                distance_from_root = self.path_distances[root_id][node["id"]]
                distances.append(distance_from_root)
                self.mean_end_node_distance += distance_from_root
                if distance_from_root > self.max_end_node_distance:
                    self.max_end_node_distance = distance_from_root
                num_drivers += 1
                ##########
            else:
                color = "rgba(0, 0, 200, 0.75)"
            node["color"] = color

            # make the node a triangle if the it is one of the common_time_series
            if (
                self.common_time_series
                and row["time_series_name"] in self.common_time_series
            ):
                node["borderWidth"] = 5
                node["shape"] = "triangle"

            # store description, mo_name, ticker, and driver status of time series in node
            node["description"] = str(row["time_series_description"])
            node["time_series_name"] = str(row["time_series_name"])
            node["ticker"] = str(row["ticker"])
            node["is_driver"] = str(row["is_driver"])

            # set the label to be whatever column the user decided to take labels from
            label = str(row[col_for_labels])
            # Format the label to be max n characters per line
            n = 13  # characters per line
            new_label = "\n".join([label[i : i + n] for i in range(0, len(label), n)])
            node["label"] = new_label

            # add value and units and ismm (time_series_description) attributes to node for future use
            node["amount"] = row["value"]
            node["units"] = row["unit_type"]
            node["ismm"] = ", mm" in row["time_series_description"]

            # Add value to node label
            value = ""
            if node["units"] == "currency":
                value = ":\n{}{:,.2f}".format(row["unit_symbol"], row["value"])
            elif node["units"] == "percentage":
                value = ":\n{:.2f}{}".format(row["value"], row["unit_symbol"])
            # elif node["units"] == "count":
            #     value = ":\n{:.2f} {}".format(row["value"], row["unit_symbol"])
            # elif node["units"] == "ratio":
            #     value = ":\n{:.2f} {}".format(row["value"], row["unit_symbol"])
            # elif node["units"] == "time":
            #     value = ":\n{:.2f} {}".format(row["value"], row["unit_symbol"])
            else:
                value = ":\n{:.2f} {}".format(row["value"], row["unit_symbol"])
            node["label"] += value

            # title is label without newlines
            node["title"] = node["label"].replace("\n", "")

        # reformat edges
        for edge in graph.edges:
            temp = edge["from"]
            edge["from"] = edge["to"]
            edge["to"] = temp
            # label the edge with percentages
            if self.common_size_tree:
                precedent = graph.get_node(edge["from"])
                dependent = graph.get_node(edge["to"])

                # WORKAROUND FOR MO.Lastprice ##################
                if "|" not in precedent["id"] or "|" not in dependent["id"]:
                    continue
                ################################################

                if (
                    precedent["units"] == "currency"
                    and precedent["ismm"]
                    and dependent["ismm"]
                    and precedent["level"] != dependent["level"]
                ):
                    if np.isnan(precedent["amount"]):
                        pct = 0
                    else:
                        pct = precedent["amount"] / dependent["amount"] * 100
                    edge["label"] = "{:.2f}%".format(pct)

        # reformat tree so desired time series is at the root and it is a different color
        root = graph.get_node(root_id)
        root.update({"color": "rgba(0, 200, 0, 0.75)", "size": 40})

        if self.notebook:
            graph.width, graph.height = "1000px", "1000px"

        # toggles node dragging and disables physics
        graph.toggle_drag_nodes(toggle_drag_nodes)
        graph.toggle_physics(False)

        # make sure models folder exists
        models_folder = os.path.join(
            os.path.dirname(os.path.abspath(__name__)), "models"
        )
        if not os.path.isdir(models_folder):
            os.mkdir(models_folder)

        # create path for model in models folder adjacent to this file
        model_path = os.path.join(
            self.config.default_dir,
            f"DATA/{self.ticker.split()[0]}/{self.ticker.split()[0]}_{self.time_series}_model_map.html",
        )
        self.model_path = os.path.relpath(
            model_path, start=os.path.abspath(os.path.dirname(__main__.__name__))
        )

        if self.auto_download:
            graph.write_html(self.model_path, notebook=self.notebook)

        self.nodes = graph.nodes
        self.edges = graph.edges

        # update stats
        self.mean_end_node_distance /= num_drivers
        self.std_dev_node_distance = stdev(distances)

        return graph

    # shows the model
    def show_model(self):
        return self.network.show(self.model_path)

    # Creates a dataframe of each nodes mo_name and distance from root
    def create_node_df(self):
        graph = self.network

        # root node id
        root_id = graph.nodes[0]["id"]

        # columns for dataframe
        tickers = []
        time_series_names = []
        distances_to_root = []
        is_driver_col = []
        for node in graph.nodes:
            tickers.append(node["ticker"])
            time_series_names.append(node["time_series_name"])
            distances_to_root.append(self.path_distances[root_id][node["id"]])
            is_driver_col.append(node["is_driver"])

        node_df = pd.DataFrame(
            {
                "ticker": tickers,
                "time_series_name": time_series_names,
                "distance_to_root": distances_to_root,
                "is_driver": is_driver_col,
            }
        )

        return node_df

    # lists out all the nodes
    def list_nodes(self, search=""):
        print("Nodes:")
        if self.nodes:
            for node in self.nodes:
                if re.match(f".*{search}.*", node["title"]):
                    print(node["title"])

    # creates chart of given time series:
    def create_ts_chart(self, time_series_name):
        # get needed data from dataframe
        df = self.df[self.df["time_series_name"] == time_series_name]
        df = df[df["period_name"].str.contains("Q")].sort_values("period_end_date")
        # use subset=['value'] to only drop rows with a null value
        df = df.dropna(subset=["value"])
        # NEED TO ACCOUNT FOR EMPTY DATAFRAMES
        row1 = df.iloc[0]
        title = row1["time_series_description"]
        xlabel = "Fiscal Quarter"
        ylabel = row1["time_series_description"]
        # plot data
        fig = px.line(
            df,
            x="period_name",
            y="value",
            title=title,
            labels={"period_name": xlabel, "value": ylabel},
        )
        return fig

    # shows a chart of the given time series
    def show_ts_chart(self, time_series_name):
        fig = self.create_ts_chart(time_series_name)
        fig.show()


class Model:
    # functions which are CamelCase will become Classes at some point
    def __init__(
        self,
        ticker,
        config: Config = None,
        force=False,
        extract_drivers=True,
        historical_only=False,
    ):
        self.config = config or CONFIG
        self.historical_only = historical_only
        self.ticker = ticker
        self.force = force
        self.extract_drivers = extract_drivers

        self.api_headers = get_api_headers(self.config.canalyst_api_key)
        self.gt = Getter(self.config)
        self.log = LogFile(default_dir=self.config.default_dir)

        self.set_new_uuid()

        if self.force == True:
            print("model_frame")

        self.csin, self.latest_version = get_company_info_from_ticker(
            self.ticker, self.api_headers, self.config.mds_host
        )

        self.get_model_frame()

        if self.extract_drivers == True:
            self.apply_drivers(self.force)

        if self.force == True:
            print("model_drivers")

        if self.extract_drivers == True:
            try:
                self._revenue_drivers = dot_parse(
                    self.default_df,
                    ticker=self.ticker,
                    auth_headers=self.api_headers,
                    config=self.config,
                    s3_client=self.gt,
                )
            except:
                self.log.write("failed to create drivers")

        if self.force == True:
            print("guidance")
            self.create_guidance_csv()

    def get_params(self, search_term=""):
        df = self.default_df
        if search_term != "":
            search_term = "(?i)" + search_term
            df1 = df[df["time_series_description"].str.contains(search_term)]
            df2 = df[df["time_series_name"].str.contains(search_term)]
            df = pd.concat([df1, df2])
            df = (
                df.groupby(["time_series_name", "time_series_description"])
                .first()
                .reset_index()
            )
        df = df.sort_values("time_series_name")
        return df[["time_series_name", "time_series_description"]]

    def set_params(self, list_params=[]):
        self.set_new_uuid()
        scenario_name = self.uuid
        list_changes = []
        for param in list_params:
            list_changes.append(
                {
                    "time_series": param["feature_name"],
                    "period": param["feature_period"],
                    "value_expression": {
                        "type": "literal",
                        "value": param["feature_value"],
                    },
                }
            )

        data = {"changes": list_changes, "name": scenario_name}

        response = send_scenario(
            ticker=self.ticker, data=data, mds_host=self.config.mds_host
        )

        return

    def show_tree(
        self,
        time_series="MO_RIS_REV",
        tree=True,
        notebook=True,
        common_time_series=None,
    ):
        mm = ModelMap(
            config=self.config,
            model=self,
            time_series=time_series,
            tree=tree,
            notebook=notebook,
            common_time_series=common_time_series,
        )
        self.model_map = mm
        return mm.show_model()

    def create_guidance_csv(self):
        file_ticker = self.ticker.split(" ")[0]
        path_name = f"{self.config.default_dir}/DATA/{file_ticker}/"
        os.makedirs(path_name, exist_ok=True)

        files = os.listdir(path_name)

        for filename in files:

            if "xlsx" in str(filename):
                try:
                    print("read excel for guidance")
                    df = pd.read_excel(
                        open(f"{path_name}" + filename, "rb"),
                        index_col=False,
                        sheet_name="guidance",
                    )
                except:
                    self.log.write("guidance: Excel read error")
                    return
                try:
                    save_guidance_csv(df, self.ticker, path_name)
                    return
                except:
                    self.log.write("guidance: Save guidance csv error")

    def set_new_uuid(self):
        self.uuid = datetime.datetime.now()
        self.uuid = str(self.uuid).replace(" ", "_")
        self.uuid = self.uuid.replace(":", ".")
        self.uuid = self.uuid.replace("-", "_")

    def mrq(self):
        df = self._model_frame
        df = df[df["is_historical"] == True]
        df = df[~df["period_name"].str.contains("FY")]
        df = df.sort_values("period_end_date", ascending=False)
        return pd.DataFrame(
            df.iloc[0][["period_name", "period_end_date"]]
        ).T.reset_index()[["period_name", "period_end_date"]]

    def guidance(self):
        df = self.gt.get_file(self.ticker, "guidance")
        self.guidance = df
        return df

    def get_driverlibrary(self, force=False):
        df = self.gt.get_file(self.ticker, "model_drivers")

        if df is not None and force == False:
            self.model_drivers = df
            return
        print("get drivers from model")

        df_drivers, self.df_name_index = get_drivers_from_model(
            self.ticker,
            self.api_headers,
            self.config.default_dir,
            self.config.mds_host,
            self.config.wp_host,
        )
        df_drivers = df_drivers.loc[df_drivers["historical"] == 0]
        df = (
            df_drivers.groupby("named_range")
            .first()
            .reset_index()
            .sort_values("cell")[["named_range"]]
        )

        df.columns = ["time_series_name"]
        self.model_drivers = df

        ticker = self.ticker.split(" ")[0]
        self.model_drivers.to_csv(
            f"{self.config.default_dir}/DATA/{ticker}/{self.ticker}_model_drivers.csv",
            index=False,
        )
        self.df_name_index.to_csv(
            f"{self.config.default_dir}/DATA/{ticker}/{self.ticker}_name_index.csv",
            index=False,
        )

        return

    def revenue_drivers(self, search_term="", is_driver=False):
        pd.set_option("display.max_colwidth", None)
        df = self._model_frame
        df_only_drivers = self._revenue_drivers
        df = pd.merge(
            df,
            df_only_drivers,
            how="inner",
            left_on="time_series_name",
            right_on="time_series_name_dependent",
        )
        df1 = df[
            df["time_series_description"].str.contains(
                search_term, flags=re.IGNORECASE, regex=True
            )
        ]
        df2 = df[
            df["time_series_name"].str.contains(
                search_term, flags=re.IGNORECASE, regex=True
            )
        ]
        df = pd.concat([df1, df2])
        df = df.dropna()
        df = (
            df.groupby(["time_series_name", "time_series_description"])
            .first()
            .reset_index()
        )
        df = df.drop(
            columns=[
                "period_duration_type",
                "category_type_slug",
                "time_series_slug",
                "category_type_name",
                "category_slug",
                "is_historical",
                "value",
                "period_start_date",
                "period_end_date",
                "period_name",
                "time_series_name",
                "time_series_description",
            ]
        )
        df = df.sort_values("index")
        df = df.reset_index()
        df = df.drop(columns=["index", "level_0"])
        if is_driver == True:
            df = df.loc[df["is_driver"] == True]
            return df
        return df

    def model_drivers(self, search_term=""):
        df = self._modelframe
        df_only_drivers = self.model_drivers
        df_drivers = pd.merge(
            df,
            df_only_drivers,
            how="inner",
            left_on="time_series_name",
            right_on="time_series_name",
        )
        df1 = df[
            df["time_series_description"].str.contains(
                search_term, flags=re.IGNORECASE, regex=True
            )
        ]
        df2 = df[
            df["time_series_name"].str.contains(
                search_term, flags=re.IGNORECASE, regex=True
            )
        ]
        df = pd.concat([df1, df2])
        df = (
            df.groupby(["time_series_name", "time_series_description"])
            .first()
            .reset_index()
        )
        df = df[["time_series_name", "time_series_description"]]
        return df

    # MODELSET model_frame
    def model_frame(
        self,
        time_series_name="",
        period_name="",
        is_driver="",
        pivot=False,
        mrq=False,
        period_duration_type="",
        is_historical="",
        n_periods=12,
        mrq_notation=True,
        warning=True,
    ):
        return filter_dataset(
            self._model_frame,
            time_series_name,
            period_name,
            is_driver,
            pivot,
            mrq,
            period_duration_type,
            is_historical,
            n_periods,
            mrq_notation,
            warning,
        )

    def apply_drivers(self, force=False):

        # this is a separate step for debug... should merge into model_frame

        df = self.gt.get_file(self.ticker, "model_drivers")

        if df is not None and force == False:
            self.model_drivers = df
        else:
            print("get driver library")
            self.get_driverlibrary(force=self.force)
            df = self.model_drivers

        df = df.assign(is_driver=True)
        df2 = pd.merge(
            self._model_frame,
            df,
            how="outer",
            left_on="time_series_name",
            right_on="time_series_name",
        )
        df2 = df2[df2["ticker"].notna()]
        df2[["is_driver"]] = df2[["is_driver"]].fillna(value=False)
        self._model_frame = df2

        df_index = self.gt.get_file(self.ticker, "name_index")

        if df_index is not None:
            df_index.columns = ["time_series_name", "name_index"]
        else:
            mrq = self._model_frame["MRQ"].loc[0]
            df_index = self._model_frame.loc[self._model_frame["period_name"] == mrq][
                ["time_series_name"]
            ]
            df_index["name_index"] = np.arange(len(df_index))

        self._model_frame = pd.merge(
            self._model_frame,
            df_index,
            how="outer",
            left_on="time_series_name",
            right_on="time_series_name",
        )

        self._model_frame = self._model_frame[self._model_frame["period_name"].notna()]
        return

    def get_model_frame(self):

        df_hist = self.historical_data_frame()
        df_hist = df_hist.assign(is_historical=True)
        df_hist = df_hist[~df_hist["period_name"].isna()]

        mrq = df_hist["period_name"].iloc[0]
        pd.options.mode.chained_assignment = None

        df_fwd = self.forward_data_frame()
        df_fwd = df_fwd.assign(is_historical=False)
        df_fwd = df_fwd[~df_fwd["period_name"].isna()]

        df_concat = pd.concat([df_hist, df_fwd]).sort_values("period_name")

        self._model_frame = df_concat

        mrq = self.mrq()["period_name"][0]
        self._model_frame["MRQ"] = [mrq for i in range(len(self._model_frame))]
        return

    def feature_search(self, search_term=""):
        if search_term != "":
            df = self._model_frame
            df1 = df[
                df["time_series_description"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df2 = df[
                df["time_series_name"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df = pd.concat([df1, df2])
            df = (
                df.groupby(["time_series_name", "time_series_description"])
                .first()
                .reset_index()
            )
            df = df[["time_series_name", "time_series_description"]]
        return df

    def driver_search(self, search_term=""):
        df = self.model_drivers
        if search_term != "":
            df = self._model_frame
            df_only_drivers = self.model_drivers
            df_drivers = pd.merge(
                df,
                df_only_drivers,
                how="inner",
                left_on="time_series_name",
                right_on="time_series_name",
            )
            df1 = df[
                df["time_series_description"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df2 = df[
                df["time_series_name"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df = pd.concat([df1, df2])
            df = (
                df.groupby(["time_series_name", "time_series_description"])
                .first()
                .reset_index()
            )
            df = df[["time_series_name", "time_series_description"]]
        return df

    def describe_drivers(self, filter_string=""):
        # if self.describe_drivers is not None:
        #    return self.describe_drivers
        # get the historical dataframe from candas
        df = self.historical_data_frame()
        df_only_drivers = self.model_drivers
        # merge the drivers and the historical data... and return a description of the values for each
        df_drivers = pd.merge(
            df,
            df_only_drivers,
            how="inner",
            left_on="time_series_name",
            right_on="time_series_name",
        )
        df_drivers_summary = (
            df_drivers.groupby(["time_series_name"]).describe().reset_index()
        )
        if filter_string != "":
            self.describe_drivers = df_drivers_summary
            return df_drivers_summary[
                df_drivers_summary["time_series_name"].str.contains(
                    filter_string, case=False
                )
            ]
        self.describe_drivers = df_drivers_summary
        return df_drivers_summary

    def historical_data_frame(self):  # if cache = true save locally?
        if self.force == False:
            df = self.gt.get_file(self.ticker, "historical_data")
            if df is not None:
                return df

        file_ticker = self.ticker.split(" ")[0]
        path_name = f"{self.config.default_dir}/DATA/{file_ticker}/"
        os.makedirs(path_name, exist_ok=True)

        try:
            url_hist, model_info = get_model_info(
                self.ticker,
                self.api_headers,
                self.config.default_dir,
                self.config.mds_host,
            )
        except:
            self.log.write(f"Candas: url error with {self.ticker} ticker")
            return

        crawl_args = {
            "next_url": url_hist,
            "ticker": self.ticker,
            "key_name": "results",
            "next_name": "next",
            "auth_headers": self.api_headers,
            "default_dir": self.config.default_dir,
        }

        crawl_company_pages(**crawl_args)

        dict_json = read_json(self.ticker, self.config.default_dir)

        df = json_to_df(dict_json, self.ticker)

        df.to_csv(path_name + self.ticker + "_historical_data.csv")
        df_model_info = pd.DataFrame(model_info)
        df_model_info.to_csv(path_name + self.ticker + "_model_info.csv")
        return df

    def summary(self, filter_term=""):
        pd.set_option("mode.chained_assignment", None)
        pd.set_option("display.float_format", lambda x: "%.5f" % x)

        df = pd.merge(
            self.model_frame(
                period_duration_type="fiscal_quarter",
                is_historical=False,
                warning=False,
            ),
            self.scenario_df,
            how="inner",
            left_on=[
                "ticker",
                "period_name",
                "time_series_name",
                "time_series_description",
            ],
            right_on=[
                "ticker",
                "period_name",
                "time_series_name",
                "time_series_description",
            ],
        )[
            [
                "ticker",
                "period_name",
                "time_series_name",
                "time_series_description",
                "value_x",
                "value_y",
            ]
        ]
        df.columns = [
            "ticker",
            "period_name",
            "time_series_name",
            "time_series_description",
            "default",
            "scenario",
        ]
        df["diff"] = df["scenario"].astype(float) / df["default"].astype(float)
        if filter_term != "":
            df = df[df["time_series_name"].str.contains(filter_term, case=False)]
        return df

    def forward_data_frame(self):
        if self.force == False:
            df = self.gt.get_file(self.ticker, "forecast_data")
            if df is not None:
                self.default_df = df
                return df

        file_ticker = self.ticker.split(" ")[0]
        path_name = f"{self.config.default_dir}/DATA/{file_ticker}/"
        file_name = f"{path_name}{self.ticker}_forecast_data.csv"

        if not os.path.exists(path_name):
            os.makedirs(path_name)

        if self.csin == "":
            self.csin, self.latest_version = get_company_info_from_ticker(
                self.ticker,
                self.api_headers,
                self.config.mds_host,
            )

        url = get_forecast_url(self.csin, self.latest_version, self.config.mds_host)

        res = get_request(url, self.api_headers)

        list_out = []

        for res_dict in res.json()["results"]:
            df = get_forecast_url_data(res_dict, self.ticker, self.api_headers)
            list_out.append(df)

        self.default_df = pd.concat(list_out)
        self.default_df.to_csv(file_name, index=False)

        return df

    def model_fit(self, time_series_name=""):

        if self.csin == "":
            self.csin, self.latest_version = get_company_info_from_ticker(
                self.ticker,
                auth_headers=self.api_headers,
                mds_host=self.config.mds_host,
            )

        url = get_forecast_url(self.csin, self.latest_version, self.config.mds_host)

        scenario_url = (
            f"{self.config.mds_host}/"
            f"{SCENARIO_URL.format(csin=self.csin, version=self.latest_version)}"
        )

        scenario_response = get_request(scenario_url, headers=self.api_headers)

        scenario_json = scenario_response.json()
        scenario_id_url = map_scenario_urls(scenario_json).get(self.uuid)

        if scenario_id_url is None:
            self.log.write(
                "Scenario ID for " + scenario_url + " is None.  Perhaps max scenarios."
            )
            return

        print(self.ticker + " scenario_id_url: " + str(scenario_id_url))

        if time_series_name != "":

            url = scenario_id_url + "time-series/?name=" + time_series_name

            res_loop = get_request(url, self.api_headers)
            url = res_loop.json()["results"][0]["self"]
            res_loop = get_request(url, self.api_headers)
            url = res_loop.json()["forecast_data_points"]
            res_loop = get_request(url, self.api_headers)
            res_data = res_loop.json()["results"]
            dict_out = {}
            list_out = []
            for res_data_dict in res_data:
                dict_out["time_series_slug"] = res_data_dict["time_series"]["slug"]
                dict_out["time_series_name"] = res_data_dict["time_series"]["names"][0]
                dict_out["time_series_description"] = res_data_dict["time_series"][
                    "description"
                ]
                dict_out["category_slug"] = res_data_dict["time_series"]["category"][
                    "slug"
                ]
                dict_out["category_type_slug"] = res_data_dict["time_series"][
                    "category"
                ]["type"]["slug"]
                dict_out["category_type_name"] = res_data_dict["time_series"][
                    "category"
                ]["type"]["name"]
                dict_out["unit_description"] = res_data_dict["time_series"]["unit"][
                    "description"
                ]
                dict_out["unit_symbol"] = res_data_dict["time_series"]["unit"]["symbol"]
                dict_out["period_name"] = res_data_dict["period"]["name"]
                dict_out["period_duration_type"] = res_data_dict["period"][
                    "period_duration_type"
                ]
                dict_out["period_start_date"] = res_data_dict["period"]["start_date"]
                dict_out["period_end_date"] = res_data_dict["period"]["end_date"]
                dict_out["value"] = res_data_dict["value"]
                dict_out["ticker"] = self.ticker
                df = pd.DataFrame.from_dict(dict_out, orient="index").T
                list_out.append(df)
            self.scenario_df = pd.concat(list_out)
            return

        scenario_id_url = scenario_id_url + "forecast-periods/"

        scenario_response = get_request(scenario_id_url, headers=self.api_headers)
        all_df = []

        all_df = Parallel(n_jobs=num_cores)(
            delayed(get_scenario_url_data)(res_dict, self.ticker)
            for res_dict in scenario_response.json()["results"]
        )
        self.scenario_df = pd.concat(all_df)
        print("Done")
        return
