import os
import pandas as pd


class NS(object):
    def __repr__(self):
        return str(self.__dict__)


class DataLoader(object):
    def __init__(self, fnam):
        self.fnam = os.path.expanduser(fnam)

    def load_xls(self):
        self.data = pd.read_excel(self.fnam)
        return self.post_load()

    def post_load(self):
        self.data.columns = self.data.columns.str.lower()
        self.data.fillna(0)
        return self

    def get_row(self, idx):
        return self.data.iloc[[idx]]

    def get_val(self, row, nam):
        cell = row[nam.lower()]
        val = cell.values[0]
        return val if pd.notna(val) else None

    def get_cols(self, row, cols):
        result = NS()
        for nam in cols:
            val = self.get_val(row, nam)
            norm = nam.lower().replace(" ", "_")
            setattr(result, norm, val)
        return result


common_data = [
    "Manufacturer",
    "Model",
    "Year",
    "EAN",
]


def combined_cols(cols):
    c = list(common_data)
    c.extend(cols)
    return c


class RimDataLoader(DataLoader):
    def get_dims(self, idx):
        row = self.get_row(idx)
        return self.get_cols(row, combined_cols(["Holes", "ERD"]))


class HubDataLoader(DataLoader):
    def get_dims(self, idx):
        row = self.get_row(idx)
        return self.get_cols(
            row,
            combined_cols(
                [
                    "Holes",
                    "Spoke Hole",
                    "Flange Diameter Left",
                    "Flange Diameter Right",
                    "Flange Distance Left",
                    "Flange Distance Right",
                ]
            ),
        )
