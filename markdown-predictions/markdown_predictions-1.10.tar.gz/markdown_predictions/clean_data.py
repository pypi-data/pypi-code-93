""" This script cleans the dataframe """
from types import prepare_class
from numpy.core.numeric import True_
import pandas as pd

from markdown_predictions.parse_data import LoadSalesData


PRICE_COLS = ["price_PRE", "price_POST"]
TARGET_SALES = ["quantity_sold_POST", "quantity_sold_sub1_POST"]


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

    def clean_up_symbols(self, x):
        """ Remove symbols and commas from columns """
        x = x.replace(',', '').replace('€', '')
        if '%' in x:
            x =  str(float(x.replace('%', '')) / 100.)
        return x

    def make_columns_numeric(self):
        """ Try to make columns numeric, else leave as original type """
        for col in self.df.columns:
            try:
                self.df[col] = self.df[col].apply(lambda x: self.clean_up_symbols(x)).astype(float)
                self.numeric_cols.append(col)
            except ValueError as e:
                # print(e)
                self.object_cols.append(col)

    def add_2week_sales(self):
        """ Add Sales Target """
        self.df["two_week_sales"] = self.df[TARGET_SALES].sum(axis=1)
        self.df.drop(TARGET_SALES, axis=1, inplace=True)

    def clean_up_data(self):
        """ Clean up the dataframe """
        self.drop_rows_without_reference()
        self.drop_row_with_missing_entries()
        self.replace_decimal_in_price_cols()
        self.make_columns_numeric()
        self.add_2week_sales()

if __name__ == "__main__":
    # Load in the data locally into a single dataframe
    loaded_data = LoadSalesData.load_in_files("raw_data")
    # Initiate pre-processing class instance
    pre_processor = PreProcessor(df=loaded_data.sales_data)
    pre_processor.clean_up_data()
