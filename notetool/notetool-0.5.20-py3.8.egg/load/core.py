import os
import pickle

import pandas as pd


class DataLoadAndSave:
    def __init__(self, path_dir):
        self.path_dir = path_dir

    def file_path(self, filename):
        return os.path.join(self.path_dir, filename)

    def save_pickle(self, data, filename):
        with open(self.file_path(filename), 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    def save_json(self, data, filename):
        data.to_json(self.file_path(filename))

    def save_csv(self, data, filename):
        data.to_csv(self.file_path(filename))

    def load_pickle(self, filename):
        with open(self.file_path(filename), 'rb') as f:
            data = pickle.load(f)
            return data

    def load_json(self, filename):
        return pd.read_json(self.file_path(filename))

    def load_csv(self, filename):
        return pd.read_csv(self.file_path(filename))

    def save(self, data, filename):
        if '.pkl' in filename:
            self.save_pickle(data, filename)
        elif '.csv' in filename:
            self.save_csv(data, filename)
        elif '.json' in filename:
            self.save_json(data, filename)
        else:
            self.save_pickle(data, filename)

    def load(self, filename):
        if '.pkl' in filename:
            return self.load_pickle(filename)
        elif '.csv' in filename:
            return self.load_csv(filename)
        elif '.json' in filename:
            return self.load_json(filename)
        else:
            return self.load_pickle(filename)

    def load_save(self, filename, fun=None, overwrite=False):
        if os.path.exists(self.file_path(filename)) and not overwrite:
            return self.load(filename)
        else:
            data = fun()
            self.save(data, filename)
            return data
