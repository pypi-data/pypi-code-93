__author__ = 'yuquanfeng'

"""
使用该库方法，需要传入数据集的根目录，存放图片资源的根目录，以及存放图片对应类别的csv文件，层级如下所示
--dataset\
----imgs\
------xxx.jpg
------subdir\
--------xxx.jpg
----label.csv

===================================
label.csv文件内容如下
image, labels
800113bb65efe69e.jpg, healthy

针对不同的label.csv文件，你需要继承DataLabel类之后，重写其_get_files_label()方法，
该方法返回(img_ids, label_ids, classes)元组

具体示例，参考 KagglePlantPathologyDataLabel类
===================================
具体使用示例，参考 get_split_data方法
"""

import os
import numpy as np
import pandas as pd
from tqdm import tqdm


class DataLabel:
    def __init__(self, files_dir, output_dir, label_csv_file_path, ratio: tuple = (7, 2, 1)):
        """
        初始化
        :param files_dir: 存放图片的根目录
        :param output_dir: 输出文件的根目录
        :param label_csv_file_path: 保存文件id和类别对应的文件路径
        :param ratio: 设置拆分比例，可选，默认(7, 2, 1)
        """
        self.files_dir = files_dir
        self.output_dir = output_dir
        self.label_csv_file_path = label_csv_file_path
        self.ratio = ratio
        self.paths = []  # 用来保存所有文件的绝对路径

    def split_dataset(self):
        """
        首先需要获取到文件的id列表img_ids，以及其对应标签label_ids，类别名称classes列表，
        请继承本类之后，重写get_files_label方法，该方法返回(img_ids, label_ids, classes)元组
        """
        print('-------------拆分数据集--------------')
        img_ids, label_ids, classes = self._get_files_label()
        train_idx, valid_idx, test_idx = self._get_random_idx(len(img_ids), self.ratio)
        train_df = self._get_random_dataset((img_ids, label_ids, classes), train_idx)
        valid_df = self._get_random_dataset((img_ids, label_ids, classes), valid_idx)
        test_df = self._get_random_dataset((img_ids, label_ids, classes), test_idx)

        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        train_df.to_csv(os.path.join(self.output_dir, 'train_label.csv'), index=False)
        valid_df.to_csv(os.path.join(self.output_dir, 'valid_label.csv'), index=False)
        test_df.to_csv(os.path.join(self.output_dir, 'test_label.csv'), index=False)
        print(f'-------------训练，验证，测试集的拆分长度为{len(train_df)},{len(valid_df)},{len(test_df)}--------------')

    def get_files_path(self, postfix=None):
        """
            通过传入文件根目录self.files_dir，可以找到该目录下所有的文件，返回文件路径列表。
            可选的postfix：指定扫描的文件后缀名

            :param: postfix: 传入文件后缀
            """
        print('-------------获取文件绝对路径列表--------------')
        result = []
        for root_path, dirs, files in os.walk(self.files_dir):
            for file in tqdm(files):
                if postfix and os.path.splitext(file)[1] == postfix:
                    result.append(os.path.join(root_path, file))
                else:
                    result.append(os.path.join(root_path, file))
        print(f'-------------共获取{len(result)}个{postfix}文件的绝对路径--------------')
        self.paths = result
        return result

    def _get_files_label(self):
        raise NotImplemented

    @staticmethod
    def _get_random_idx(dataset_size, ratio=(7, 2, 1)):
        """
        获取随机生成的索引列表
        :param dataset_size: 总的数据集的尺寸大小
        :param ratio: 拆分的比例
        :return: 训练集，验证集，测试集的随机索引列表
        """
        assert ratio[0] + ratio[1] + ratio[2] == 10, "总的比例之和必须等于10"
        train_split = ratio[0] * 0.1
        valid_split = ratio[1] * 0.1
        random_seed = 777

        indices = list(range(dataset_size))
        np.random.seed(random_seed)
        np.random.shuffle(indices)

        split1 = int(np.floor(train_split * dataset_size))
        split2 = int(np.floor((train_split + valid_split) * dataset_size))

        return indices[:split1], indices[split1:split2], indices[split2:]

    @staticmethod
    def _get_random_dataset(datasets, random_idx):
        img_ids, label_ids, classes = datasets
        img_ids, label_ids, classes = np.array(img_ids), np.array(label_ids), np.array(classes)
        train_img_ids, train_label_ids, train_classes = img_ids[random_idx], label_ids[random_idx], classes[random_idx]

        train_data = {'id': train_img_ids, 'label': train_label_ids, 'class_y': train_classes}
        return pd.DataFrame(train_data)


class KagglePlantPathologyDataLabel(DataLabel):
    def __init__(self, files_dir, output_dir, label_csv_file_path, ratio: tuple = (7, 2, 1)):
        super(KagglePlantPathologyDataLabel, self).__init__(files_dir, output_dir, label_csv_file_path, ratio)

    def _get_files_label(self):
        assert len(self.paths) > 0, "请先执行get_files_path()方法获取文件绝对路径列表"

        print(f'-----------获取文件的label-----------')
        label_df = pd.read_csv(self.label_csv_file_path)
        count = 0
        img_ids = []
        label_ids = []
        classes = []

        for idx in tqdm(range(len(self.paths))):
            path = self.paths[idx]
            img_name = path.split('/')[-1]
            df = label_df.loc[label_df['image'] == img_name]

            if len(df['labels']) == 1:
                category = df['labels'].item()
            else:
                continue

            if category == 'healthy':
                label = 0
            elif category == 'scab':
                label = 1
            elif category == 'frog_eye_leaf_spot':
                label = 2
            elif category == 'rust':
                label = 3
            elif category == 'complex':
                label = 4
            elif category == 'powdery_mildew':
                label = 5
            else:
                continue

            count += 1
            img_ids.append(path)
            label_ids.append(label)
            classes.append(category)

        print(f'-----------一共匹配了 {count} 个文件-----------')
        return img_ids, label_ids, classes


def get_split_data(SubClass,
                   root,
                   files_dir_name,
                   output_dir_name,
                   label_csv_name,
                   postfix=None,
                   ratio: tuple = (7, 2, 1)):
    """
    :param SubClass: DataLabel的子类
    :param root: 数据集根目录
    :param files_dir_name: 资源文件所在的根目录名称
    :param output_dir_name: 输出文件根目录名称
    :param label_csv_name: 文件id对应的标签的csv文件名称
    :param postfix: 文件后缀名，可选
    :param ratio: 设置拆分比例，可选，默认(7, 2, 1)
    """
    assert issubclass(SubClass, DataLabel), "SubClass必须继承自DataLabel类"

    # 1 设置文件根目录
    files_dir = os.path.join(root, files_dir_name)
    output_dir = os.path.join(root, output_dir_name)
    label_csv_path = os.path.join(root, label_csv_name)

    # 2 获取对象实例
    data_label = SubClass(files_dir, output_dir, label_csv_path, ratio)

    # 3 获取文件绝对路径列表
    data_label.get_files_path(postfix=postfix)

    # 4 将文件路径和其label一一对应，并拆分为训练，验证，测试三个子集，分别保存在csv文件中
    data_label.split_dataset()


if __name__ == '__main__':
    # get_split_data(SubClass=KagglePlantPathologyDataLabel,
    #                root='/stu01/datasets/Kaggle_plant_pathology/',
    #                files_dir_name='train_images',
    #                output_dir_name='output',
    #                label_csv_name='train.csv',
    #                postfix='.jpg'
    #                )
    """
    参考输出1：
    -------------获取文件绝对路径列表--------------
100%|██████████████████████████████████| 18632/18632 [00:00<00:00, 59746.39it/s]
100%|███████████████████████████████████████████| 1/1 [00:00<00:00, 9799.78it/s]
-------------共获取18633个.jpg文件的绝对路径--------------
-------------拆分数据集--------------
-----------获取文件的label-----------
100%|████████████████████████████████████| 18633/18633 [00:41<00:00, 448.52it/s]
-----------一共匹配了 17277 个文件-----------
-------------训练，验证，测试集的拆分长度为12093,3456,1728--------------
    """

    get_split_data(SubClass=KagglePlantPathologyDataLabel,
                   root='/stu01/datasets/Kaggle_plant_pathology/',
                   files_dir_name='train_images',
                   output_dir_name='output',
                   label_csv_name='train.csv',
                   postfix='.jpg',
                   ratio=(8, 1, 1)
                   )
    """
    参考输出2：
    -------------获取文件绝对路径列表--------------
100%|█████████████████████████████████| 18632/18632 [00:00<00:00, 349528.46it/s]
100%|██████████████████████████████████████████| 1/1 [00:00<00:00, 26546.23it/s]
-------------共获取18633个.jpg文件的绝对路径--------------
-------------拆分数据集--------------
-----------获取文件的label-----------
100%|████████████████████████████████████| 18633/18633 [00:27<00:00, 675.77it/s]
-----------一共匹配了 17277 个文件-----------
-------------训练，验证，测试集的拆分长度为13821,1728,1728--------------
    """
