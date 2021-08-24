import random

from .dataset import Dataset


class DataLoader(object):

    def __init__(self, dataset, shuffle=False):
        self.count = 0
        self.dataset = dataset
        self.idxs = [i for i in range(len(self.dataset))]

        if shuffle:
            random.shuffle(self.idxs)

        if not isinstance(dataset, Dataset):
            raise RuntimeError(f"dataset not Intellino Dataset Class {type(dataset)}")

    def __iter__(self):
        return self

    def __next__(self):
        if self.count >= len(self.dataset):
            raise StopIteration
        else:
            elm = self.dataset[self.idxs[self.count]]
            self.count += 1
            return elm

    def __len__(self):
        return len(self.dataset)