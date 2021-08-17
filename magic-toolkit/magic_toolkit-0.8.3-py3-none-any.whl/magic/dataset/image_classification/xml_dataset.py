import glob
import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from ..dataset import Dataset
import xml.etree.ElementTree as ET

class XMLDataset(Dataset):
    """
    1. parse xml dataset
    2. xml format:
         train
          -- image
          -- label
         test
          -- image
          -- label
    """

    def __init__(self, dataset_path, transform,
                 xmlKey=None):
        # pass xml key for parsing
        self.xmlKey = xmlKey
        if self.xmlKey is None:
            self.xmlKey = {"object": "object", "class": "name"}

        self.dataset_path = dataset_path
        self.transform = transform
        assert os.path.exists(self.dataset_path)
        self.img_dir = os.path.join(dataset_path, "image")
        self.label_dir = os.path.join(dataset_path, "label")
        assert os.path.exists(self.img_dir)
        assert os.path.exists(self.label_dir)

        # get all paths of image in directory
        self.img_paths = []
        img_suffix = ["*.jpg", "*.png"]
        for fmt in img_suffix:
            ret = glob.glob(os.path.join(self.img_dir, fmt))
            self.img_paths.extend(ret)

    def __getitem__(self, index):
        sample = self.get_sample(index)
        # preprocess, data argument
        if self.transform:
            data = self.transform(sample)
            assert isinstance(data, dict), "transform must return dict"
            assert len(data) > 0
            return data
        else:
            return sample

    def __len__(self):
        return len(self.img_paths)

    def get_sample(self, index):
        img_path = self.img_paths[index]
        img_name = ".".join(os.path.basename(img_path).split(".")[:-1])

        # get ground truth from txt
        xml_path = os.path.join(self.label_dir, img_name + ".xml")
        assert os.path.exists(xml_path), "label error: {} does not exist".format(xml_path)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        lines = list()
        for obj in root.iter(self.xmlKey["object"]):
            cls = obj.find(self.xmlKey["class"]).text
            lines.append([cls])

        sample = SampleForClf()
        """catch exception to prevent training from terminating"""
        try:
            sample.image = cv2.imread(img_path)
            sample.label = np.array(lines, dtype=np.str)
            assert isinstance(sample.label, np.ndarray), print(lines)
        except Exception as err:
            print("error sample:", xml_path)
            print("error info:", err)
            print("label:", lines)
            print("-" * 100)

        return sample

    def split(self, test_size=0.3, shuffle=True):
        """return train_set, test_set"""
        train_set = XMLDataset(self.dataset_path, self.transform, self.xmlKey)
        test_set = XMLDataset(self.dataset_path, self.transform, self.xmlKey)
        train_x, test_x = train_test_split(self.img_paths, test_size=test_size, random_state=100, shuffle=shuffle)
        train_set.img_paths = train_x
        test_set.img_paths = test_x
        print("split dataset >>> train_size={}, test_size={}".format(len(train_set), len(test_set)))
        return train_set, test_set
