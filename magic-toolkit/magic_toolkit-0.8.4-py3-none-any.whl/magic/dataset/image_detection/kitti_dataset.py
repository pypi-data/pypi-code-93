import glob
import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from ..dataset import Dataset

class KittiDataset(Dataset):
    """kitti format:
         train
          -- image
              -- 001.jpg
          -- label
              -- 001.txt
    """

    def __init__(self, dataset_path, transform):
        self.dataset_path = dataset_path
        self.transform = transform
        assert os.path.exists(self.dataset_path)
        self.img_dir = os.path.join(dataset_path, "image")
        self.label_dir = os.path.join(dataset_path, "label")
        assert os.path.exists(self.img_dir)
        assert os.path.exists(self.label_dir)

        # get all paths of label file in directory
        self.label_paths = glob.glob(os.path.join(self.label_dir, "*.txt"))

    def __getitem__(self, index):
        sample = self.get_sample(index)
        # preprocess, data argument
        if self.transform:
            sample = self.transform(sample)
            assert isinstance(sample, dict), "transform must return dict"
        return sample

    def __len__(self):
        return len(self.label_paths)

    def get_sample(self, index):
        label_p = self.label_paths[index]
        filename = os.path.basename(label_p)[:-4]  # xxx.txt

        for fmt in ['.jpg', '.png', "None"]:
            img_p = os.path.join(self.img_dir, filename + fmt)
            if os.path.exists(img_p):
                break
            if fmt == "None":
                raise RuntimeError("there is not image corresponding to label: {} ".format(label_p))

        with open(label_p, 'r') as f:
            lines = [l.strip().split() for l in f.readlines()]

        sample = dict()
        sample['image'] = cv2.imread(img_p)
        sample['label'] = np.array(lines, dtype=np.str)
        return sample

    def split(self, test_size=0.3, shuffle=True):
        """return train_set, test_set"""
        train_set = KittiDataset(self.dataset_path, self.transform)
        test_set = KittiDataset(self.dataset_path, self.transform)
        train_x, test_x = train_test_split(self.label_paths, test_size=test_size, random_state=100, shuffle=shuffle)
        train_set.label_paths = train_x
        test_set.label_paths = test_x
        print("split dataset >>> train_size={}, test_size={}".format(len(train_set), len(test_set)))
        return train_set, test_set
