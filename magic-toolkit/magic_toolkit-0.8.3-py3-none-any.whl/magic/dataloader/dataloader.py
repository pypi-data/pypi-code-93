"""
Based on torch DataLoader, make batch data loading come true
"""

from torch.utils.data import DataLoader as TorchLoader
from .collate import default_collate
from .prefetch_generator import BackgroundGenerator

class DataLoader(TorchLoader):
    def __init__(self, dataset, batch_size=1, num_workers=0, shuffle=True, drop_last=False):
        """
        Data loader. Combines a dataset, and provides an iterable over the given dataset.
        :param dataset: dataset from which to load the data.
        :param batch_size: how many samples per batch to load.
        :param num_workers: how many subprocesses to use for data loading.
        :param shuffle: set to ``True`` to have the data reshuffled at every epoch.
        :param drop_last: set to ``True`` to drop the last incomplete batch.
        """

        collate_fn = default_collate

        super(DataLoader, self).__init__(dataset=dataset,
                                         batch_size=batch_size,
                                         shuffle=shuffle,
                                         num_workers=num_workers,
                                         collate_fn=collate_fn,
                                         drop_last=drop_last,
                                         pin_memory=True,
                                         sampler=None)

    def __iter__(self):
        return BackgroundGenerator(super(DataLoader, self).__iter__(), max_prefetch=2)
