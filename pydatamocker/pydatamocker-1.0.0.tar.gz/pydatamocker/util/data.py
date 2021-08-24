import os.path as osp
import pandas as pd
from pathlib import Path
import json
from ..mocker import get_config, report_progress


class Cache:

    def __init__(self):
        self.data = {}

    def insert(self, key: str, data):
        self.data[key] = { 'data': data }

    def append(self, key, data):
        if self.data.get(key) is None:
            raise ValueError(f"Data for {key} is not found")
        pd.concat(self.data[key], data)

    def get_data(self, key: str):
        if not self.data.get(key):
            return None
        return self.data[key]['data']

    def clear(self):
        self.data = {}


global_cache = Cache()


dataframe_writers = {
    '.pkl': lambda file, dataframe: dataframe.to_pickle(file, index=True),
    '.csv': lambda file, dataframe: dataframe.to_csv(file, index=False),
    '.tsv': lambda file, dataframe: dataframe.to_csv(file, sep="\t", index=False),
    '.json': lambda file, dataframe: dataframe.to_json(file, orient='table', index=False)
}

data_readers = {
    '.pkl': lambda path: pd.read_pickle(path),
    '.csv': lambda path: pd.read_csv(path)
}


get_dataset_path = lambda dataset: osp.join(osp.dirname(__file__), 'data', dataset + '.pkl')


def load_data(path: str):
    suffix = Path(path).suffix
    suffix = suffix if suffix != '' else '.csv'
    report_progress = get_config('report_progress')
    report_progress and print(f"Loading dataset at {path} ...")
    data = global_cache.get_data(path)
    if data is None:
        data = data_readers[suffix](path)
        global_cache.insert(path, data)
    return data


def write_dataframe(file: str, dataframe: pd.DataFrame):
    report_progres = get_config('report_progress')
    report_progres and print(f"Dumping into file {file}...")
    file_ext = Path(file).suffix
    if file_ext == '' or not file_ext in dataframe_writers.keys():
        file_ext = '.csv'
    dataframe_writers[file_ext](file, dataframe)
    report_progres and print("Done!")


def load_json(file) -> dict:
    f = open(file, 'rt') if type(file) is str else file
    return json.load(f)


def write_json(obj: dict, path: str, pretty: str, indent: int):
    with open(path, 'wt', ) as f:
        json.dump(obj, f, indent=(indent if pretty else None))
