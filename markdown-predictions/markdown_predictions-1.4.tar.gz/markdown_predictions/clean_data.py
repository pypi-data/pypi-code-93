""" This script cleans the dataframe """
from types import prepare_class
from numpy.core.numeric import True_
import pandas as pd

from markdown_predictions.parse_data import LoadSalesData


PRICE_COLS = ["price_PRE", "price_POST"]
SYMBOLS_TO_REMOVE = ["€", "%"]


class PreProcessor:
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = []
        self.object_cols = []
    
    def drop_rows_without_reference(self):
        """ If no product reference drop row - likely to be the total rows """
        self.df = self.df[self.df.reference_PRE.notnull()]
    
    def drop_row_with_missing_entries(self):
        """ Drop all rows with a '-' within them """
        self.df = self.df[~(self.df == '-').any(axis=1)]
    
    def replace_decimal_in_price_cols(self):
        """ Replace the comma with a decimal point in price columns """
        self.df[PRICE_COLS] = self.df[PRICE_COLS].replace({r',': '.'}, regex=True)

    def remove_symbols(self):
        """ Replace symbols in columns, otherwise cannot convert to float """
        for symbol in SYMBOLS_TO_REMOVE:
            self.df = self.df.replace({rf'([ +]?){symbol}': ''}, regex=True)
        
    def make_columns_numeric(self):
        """ Try to make columns numeric, else leave as original type """
        for col in self.df.columns:
            try:
                self.df[col] = self.df[col].replace({r',': ''}, regex=True).astype(float)
                self.numeric_cols.append(col)
            except ValueError as e:
                # print(e)
                self.object_cols.append(col)
    
    def clean_up_data(self):
        """ Clean up the dataframe """
        self.drop_rows_without_reference()
        self.drop_row_with_missing_entries()
        self.remove_symbols()
        self.replace_decimal_in_price_cols()
        self.make_columns_numeric()        
                

if __name__ == "__main__":
    # Load in the data locally into a single dataframe
    loaded_data = LoadSalesData.load_in_files("raw_data")
    # Initiate pre-processing class instance
    pre_processor = PreProcessor(df=loaded_data.sales_data)
    pre_processor.clean_up_data()
