import glob
import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from ..dataset import Dataset
import json

class JsonDataset(Dataset):
    """
    dataset format:
    train
     -- image.jpg
     -- image.json
    """

    def __init__(self, dataset_path, transform):
        self.dataset_path = dataset_path
        self.transform = transform
        assert os.path.exists(self.dataset_path)
        # get all paths of json in directory
        self.json_paths = glob.glob(os.path.join(self.dataset_path, "*.json"))

        # check annotation
        # for json_p in self.json_paths:
        #     self.get_annotation_info(json_p)

    def __getitem__(self, index):
        sample = self.get_sample(index)
        # preprocess, data argument
        if self.transform:
            sample = self.transform(sample)
            assert isinstance(sample, dict), "transform must return dict"
        return sample

    def __len__(self):
        return len(self.json_paths)

    def get_sample(self, index):
        # match json with image path, ensure exists
        json_path = self.json_paths[index]
        labels = self.get_annotation_info(json_path)

        filename = json_path[:-4]  #xxx.json
        for fmt in ['jpg', 'png', None]:
            if fmt is None:
                raise RuntimeError("there is not image corresponding to label: {} ".format(json_path))
            img_p = os.path.join(self.dataset_path, filename + fmt)
            if os.path.exists(img_p):
                break


        # sample = {"image": np.ndarray, "label": np.ndarray}
        sample = dict()
        sample['image'] = cv2.imread(img_p)
        sample['label'] = np.array(labels, dtype=np.str)
        return sample


    def get_annotation_info(self, json_path):

        with open(json_path) as f:
            js = json.load(f)

        # get infomation from json
        labels = []
        for elem in js["shapes"]:
            cls = elem['label']
            x1, y1 = elem['points'][0]
            x2, y2 = elem['points'][1]
            labels.append([cls, x1, y1, x2, y2])

        return labels

    def split(self, test_size=0.3, shuffle=True):
        """return train_set, test_set"""
        train_set = JsonDataset(self.dataset_path, self.transform)
        test_set = JsonDataset(self.dataset_path, self.transform)
        train_x, test_x = train_test_split(self.json_paths, test_size=test_size, random_state=100, shuffle=shuffle)
        train_set.json_paths = train_x
        test_set.json_paths = test_x
        print("split dataset >>> train_size={}, test_size={}".format(len(train_set), len(test_set)))
        return train_set, test_set
