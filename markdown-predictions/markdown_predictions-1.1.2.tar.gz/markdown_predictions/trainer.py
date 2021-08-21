from markdown_predictions.clean_data import PreProcessor
from markdown_predictions.parse_data import LoadSalesData

import pandas as pd
import os


def get_data(data_path: str) -> pd.DataFrame:
    """ Load in and clean the data """
    load_data = LoadSalesData.load_in_files(data_path)
    pre_processor = PreProcessor(df=load_data.sales_data)
    pre_processor.clean_up_data()
    
    return pre_processor.df

def get_path():
    print(os.listdir())


if __name__ == "__main__":
    print("HELLO 🥸🥝")
    print(get_data("raw_data"))