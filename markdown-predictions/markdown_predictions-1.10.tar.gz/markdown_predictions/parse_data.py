""" Reads in the sales data and loads into a pandas dataframe """
import collections
import glob
from json import encoder
import re
import os
import logging
import pandas as pd

from markdown_predictions.selection import COLUMN_SELECTION, COLUMN_MAPPING


class LoadSalesData:
    
    def __init__(self, sales_data: pd.DataFrame):
        self.sales_data = sales_data
    
    @staticmethod
    def extract_season(file_path: str, file_name: str):
        """ Regex the file name to extract the season """
        # Define the regex expression
        regex_expr = re.compile(rf"{file_path}\/(?P<season>\w+) W.+")
        m = regex_expr.search(file_name)
            
        if m:
            return m.group('season')
        else:
            logging.critical(f"Season cannot be extracted from {file_name}.")
            return None

    @staticmethod
    def read_in_files(file_path: str, pre_post_toggle: str, column_mapping: dict, selected_columns: dict):
        """ Read in files from local directory """
        all_sales_data = []
        
        for seasonal_file in glob.glob(f'{file_path}/*{pre_post_toggle}*'):
            logging.info(f"Reading file: {seasonal_file}")
            
            # Parse csv into dataframe
            seasonal_data = pd.read_csv(seasonal_file, index_col=None, encoding='utf-8')

            # Remove all escape characters
            seasonal_data.columns = [col.replace('\r','').replace('\n','').lower() for col in seasonal_data.columns]
            
            # Rename the columns
            seasonal_data.rename(columns=column_mapping, inplace=True)
            
            # If not all selected columns in the csv, report & exit.
            if not set(seasonal_data.columns).issuperset(set(selected_columns)):
                print(f"Not all selected columns present in csv file: {seasonal_file}.")
                print(f"Missing columns: {set(selected_columns).difference(set(seasonal_data.columns))}\nExiting.")
                exit(1)
            
            # Select the columns
            seasonal_data = seasonal_data[selected_columns]
            
            # Add season as a column to the dataframe
            season = LoadSalesData.extract_season(file_path=file_path, file_name=seasonal_file)
            if not season:
                # If season unable to be extracted skip
                continue
            seasonal_data['season'] = season
            
            # Add suffix
            seasonal_data = seasonal_data.add_suffix(suffix=f"_{pre_post_toggle}")
            all_sales_data.append(seasonal_data)

        return pd.concat(all_sales_data, axis=0, ignore_index=True)
    
    @staticmethod
    def make_dict_lowercase(input_dict: dict):
        lower_case_dict = {}
        for k, v in input_dict.items():
            lower_case_dict[k.lower()] = v  
        return lower_case_dict

    @classmethod
    def load_in_files(cls, file_path: str):
        """ Load in Files """
        mapping = LoadSalesData.make_dict_lowercase(COLUMN_MAPPING)
        
        pre_sales_data = LoadSalesData.read_in_files(file_path=file_path, pre_post_toggle="PRE", column_mapping=mapping, selected_columns=COLUMN_SELECTION["PRE"])
        post_sales_data = LoadSalesData.read_in_files(file_path=file_path, pre_post_toggle="POST", column_mapping=mapping, selected_columns=COLUMN_SELECTION["POST"])
        
        sales_data = pd.merge(pre_sales_data,
                              post_sales_data,
                              left_on=[key + "_PRE" for key in COLUMN_SELECTION["reference_keys"]] ,
                              right_on=[key + "_POST" for key in COLUMN_SELECTION["reference_keys"]],
                              how="inner")

        sales_data.drop(columns=["season_POST"], inplace=True)
        return cls(sales_data)


if __name__ == "__main__":
    loaded_data = LoadSalesData.load_in_files("raw_data")
