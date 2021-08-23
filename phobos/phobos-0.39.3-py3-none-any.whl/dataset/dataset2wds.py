import os
import webdataset as wds
import math
import pickle
import json
import glob
import tqdm

from webdataset import ShardWriter
from torch.utils.data import Dataset


class Dataset2WebDataset:
    r"""
    Creates Posix Tar shards for DataStore(datastore.granular.ai) for torch.utils.data.Dataset

    Here, key_names should be in

        **class** :         ["cls", "cls2", "class", "count", "index", "inx", "id"]
    
        **text** :          ["txt", "text", "transcript"]
    
        **image** :         ["png", "jpg", "jpeg", "img", "image", "pbm", "pgm", "ppm"]

        **image_path** :    ["path"]

        **bytes** :         ["bytes"]
    
        **pickle_object** : ["pyd", "pickle"]
    
        **torch_object** :  ["pth"]
    
        **numpy.ndarray** : ["npy"]  don't use not stable
    
        **json_dict** :     ["json", "jsn"]

    Parameters
    ----------
    dataset : `torch.utils.data.Dataset <https://pytorch.org/docs/stable/data.html#torch.utils.data.Dataset>`_
        Dataset to convert
    key_names : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        Ordered list for the items returned by the input dataset iterator
    transforms : `object <https://docs.python.org/3/reference/datamodel.html#objects-values-and-types>`_
        Transforms object to be saved on datastore for the input dataset
    mode : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        Dataset mode type = train/val/test
    shard_size : `int <https://docs.python.org/3/library/functions.html#int>`_
        Upper bound on shard memory size in GBs, default = 10GB

    Examples
    --------
    Please check `here <https://github.com/granularai/phobos/blob/develop/examples/dataset2wds/Example.ipynb>`_ 

    """
    def __init__(self, 
            dataset: Dataset, 
            keys: list, 
            transforms: object, 
            mode:str = 'train', 
            shard_size:int = 10) -> None:
        self.keys = keys
        self.dataset = dataset
        self.mode = mode
        self.transforms = transforms
        self.index_len = int(math.log10(len(self.dataset)))+1 if len(self.dataset) > 0 else 1
        
        shard_size = ((shard_size << 10) << 10) << 10
        sz_ = self.getSampleSize()
        self.sample_size = sz_
        self.samples_per_shard = int(shard_size // sz_)

        print(f"samples_per_shard:{self.samples_per_shard} sample_size_bytes:{self.sample_size}")

    def getBytes(self, path):
        with open(path, 'rb') as fp:
            return fp.read()

    def getBytesLen(self, stream):
        return len(stream)
    
    def getSampleSize(self):
        index = 1
        items = self.dataset[0]
        with ShardWriter('tmp-%01d.tar', maxcount=1) as sink:
            sample = {
                "__key__": str(index).zfill(self.index_len)
            }
            for key, val in zip(self.keys, items):
                if type(val) == str and key.split('.')[-1] == "path":
                    val = self.getBytes(val)
                sample[key] = val
            sink.write(sample)
        with open("tmp-0.tar", 'rb') as fp:
            fp.seek(0, os.SEEK_END)
            sz_ = fp.tell()
        os.remove("tmp-0.tar")     
        return sz_

    def writeShards2Local(self, out_path:str = "./"):
        r"""
        Writes shards on local filesystem

        Parameters
        ----------
        out_path : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
            Output path for writing shards
        """
        shards_out = out_path+"/"+f"{self.mode}-%0{self.index_len}d.tar"
        with ShardWriter(shards_out, 
            maxcount = self.samples_per_shard) as sink:
            for index, items in tqdm.tqdm(enumerate(self.dataset)):
                sample = {
                    "__key__" : str(index).zfill(self.index_len)
                }
                for key,val in zip(self.keys,items):
                    if type(val) == str and key.split('.')[-1] == "path":
                        val = self.getBytes(val)
                    sample[key] = val
                sink.write(sample)
                if index == len(self.dataset)-1:
                    break
        transform_out = out_path +"/transforms.pkl"
        if self.transforms is not None:
            with open(transform_out,'wb') as fp:
                pickle.dump(self.transforms,fp)
        metadata_out = out_path + f"/metadata_{self.mode}.json"
        tar_last = sorted(glob.glob(out_path+"/"+self.mode+"-*.tar"))[-1].split('-')[-1].split('.')[0]
        with open(metadata_out, 'w') as fp:
            json.dump({
                "transforms": "transforms.pkl",
                "url_posix_path": self.mode+"-{"+str(0).zfill(
                    self.index_len)+".."+tar_last+"}.tar",
                "mode": self.mode,
                "shards_count": tar_last,
                "num_samples": len(self.dataset),
                "keys": self.keys,
                "samples_per_shard": self.samples_per_shard
            }, fp)
