import os
import json
import pickle
import gzip
import multiprocessing as mp
from itertools import repeat, starmap
import numpy as np
from torch.utils.data import Dataset

from indexed_file import indexed_file


def pickle_and_compress(data):
    return gzip.compress(pickle.dumps(data))


def decompress_and_unpickle(data):
    return pickle.loads(gzip.decompress(data))


_global_fd = None


def _init(directory):
    # pylint: disable=global-statement
    global _global_fd
    _global_fd = indexed_file(directory, 'rb')


def _close():
    # pylint: disable=global-statement
    global _global_fd
    if _global_fd is not None:
        _global_fd.close()
    _global_fd = None


def _read_pickle_entry(index, keys):
    entry_bytes = _global_fd.read_entry(index)
    ret = decompress_and_unpickle(entry_bytes)
    if keys is not None:
        ret = {k: ret[k] for k in keys}
    return ret


def _read_all_entries_single_process(directory, indices, keys):
    _init(directory)
    ret = list(starmap(_read_pickle_entry, zip(indices, repeat(keys))))
    _close()
    return ret


def _read_all_entries_multi_process(directory, indices, keys, num_workers):
    # pylint: disable=no-member
    if num_workers is None:
        if hasattr(os, 'sched_getaffinity'):
            num_workers = len(os.sched_getaffinity(0))
        else:
            num_workers = os.cpu_count()
    with mp.Pool(num_workers, initializer=_init, initargs=(directory, )) as pool:
        return pool.starmap(_read_pickle_entry, zip(indices, repeat(keys)))


def read_pickle_dataset(directory, *, indices=None, keys=None, random_samples=None, seed=42, num_workers=None):
    with indexed_file(directory, 'rb') as fd:
        num_entries = len(fd)
    if random_samples is not None:
        np.random.seed(seed)
        if indices is not None:
            if len(indices) > random_samples:
                indices = np.random.choice(indices, random_samples, replace=False)
        else:
            if num_entries > random_samples:
                indices = np.random.choice(num_entries, random_samples, replace=False)

    if indices is None:
        indices = np.arange(num_entries)

    if num_workers == 0:
        return _read_all_entries_single_process(directory, indices, keys)
    return _read_all_entries_multi_process(directory, indices, keys, num_workers)


def write_pickle_dataset(directory, iterator):
    with indexed_file(directory, 'wb') as fd:
        with mp.Pool() as pool:
            for output in pool.imap(pickle_and_compress, iterator, chunksize=1):
                fd.write_entry(output)


class FileDataset(Dataset):

    def __init__(self, directory, is_binary):
        self.directory = directory
        self.mode = 'rb' if is_binary else 'r'
        self.fd = None
        self.open()

    def on_worker_init(self, worker_id):
        """
        Called automatically when `worker_init_fn` is set to `freud_utils.worker_init.generic_worker_init_fn`.
        """
        # pylint: disable=unused-argument
        self.open()

    def getobject(self, content):
        raise NotImplementedError()

    def open(self):
        self.close()
        self.fd = indexed_file(self.directory, self.mode)

    def close(self):
        if self.fd is not None:
            self.fd.close()
            self.fd = None

    def __getitem__(self, index):
        return self.getobject(self.fd.read_entry(index))

    def __len__(self):
        return len(self.fd)

    def __del__(self):
        self.close()


class PickleDataset(FileDataset):

    def __init__(self, directory):
        super().__init__(directory, is_binary=True)

    def getobject(self, content):
        return decompress_and_unpickle(content)


class JSONDataset(FileDataset):

    def __init__(self, directory):
        super().__init__(directory, is_binary=False)

    def getobject(self, content):
        return json.loads(content)
