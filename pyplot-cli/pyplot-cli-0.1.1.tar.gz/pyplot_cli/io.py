import pandas as pd


class DataSet:
    _available_types = ["dat", "txt", "csv", "xls", "xlsx"]

    def __init__(self, filename: str):
        self.filename: str = filename
        self.extension: str = filename.split(".")[-1]

        if self.extension not in self._available_types:
            raise ValueError("Invalid file extension.")

        if self.extension == "xls" or self.extension == "xlsx":
            self.dataframe = self.load_excel()
        else:
            self.dataframe = self.load_txt()

        self.column_names = list(self.dataframe.keys())
        self.values = self.dataframe.values.T

    def load_excel(self):
        return pd.read_excel(self.filename)

    def load_txt(self):
        if self.extension == "csv":
            sep = ","
        else:
            sep = r"\s+"

        data = pd.read_csv(self.filename, sep=sep)
        return data
