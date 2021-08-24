""" This runs a set of unit tests on parse_data.py which extracts the sales data into dataframes """
from markdown_predictions.parse_data import LoadSalesData

def test_extract_season():
    """ This tests extracting the season from the filename """
    file_name = "raw_data/SS20 W20 PRE.csv"
    assert LoadSalesData.extract_season(file_name) == "SS20"