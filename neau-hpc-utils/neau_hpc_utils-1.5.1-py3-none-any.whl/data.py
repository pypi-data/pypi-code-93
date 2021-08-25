import torch
import cv2
import numpy as np
import pandas as pd
from torch.utils.data.dataset import Dataset
from torch.utils.data.dataloader import DataLoader
from torchvision.transforms.functional import resize
from .helper import pair


class ImgDataset(Dataset):
    def __init__(self, annotations_file, size=None, transform=None, target_transform=None):
        """
        :param annotations_file: 含有 "文件路径" 以及对应 "标签" 的csv文件名
                                eg:文件内容如下
                                    image, labels
                                    /xx/xxx/1.jpg, 0
                                    /xx/xxx/2.jpg, 1
        :param size: 对图片做resize的操作, 因为resize操作很常用，所以传入size后，直接对图片resize操作
                    支持传入整数，如 224， 也可列表[224, 224], 元组(224, 224)
        :param transform: 对图片做的变换
        :param target_transform: 对标签做的变换
        """
        self.img_label = pd.read_csv(annotations_file)
        self.size = pair(size)
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.img_label)

    def __getitem__(self, idx):
        img_path = self.img_label.iloc[idx, 0]  # 获取图片的绝对路径
        img = cv2.imread(img_path)
        img = np.transpose(img, (2, 0, 1))  # 将shape变成（c, w, h）
        img = torch.tensor(img, dtype=torch.float)

        # 获得图片的分类
        label = self.img_label.iloc[idx, 1]

        # 对图片做变换
        if self.transform:
            img = self.transform(img)
        # 只有size满足 (int, int)或者 [int, int]时，才做resize变换
        if len(self.size) == 2 and isinstance(self.size[0], int) and isinstance(self.size[1], int):
            img = resize(img, size=self.size)

        # 对标签做变换
        if self.target_transform:
            label = self.target_transform(label)

        return img, label


def get_data_loader(annotations_file, size=None,
                    transform=None, target_transform=None,
                    shuffle=False, batch_size=32, num_workers=7):
    """
    读取图片数据集的label.csv文件，将会返回一个数据集的可迭代对象。
    :param annotations_file: 含有 "文件路径" 以及对应 "标签" 的csv文件名,eg：XXX.jpg,1
    :param size: 对图片做resize的操作时的size
    :param transform: 对图片做的变换
    :param target_transform: 对标签做的变换
    :param shuffle: bool
    :param batch_size: 批大小
    :param num_workers: 处理数据的线程数
    :return: 一个数据集的可迭代对象。
    """
    img_dataset = ImgDataset(annotations_file, size, transform, target_transform)
    img_dataloader = DataLoader(img_dataset, batch_size=batch_size,
                                num_workers=num_workers, shuffle=shuffle)
    return img_dataloader

