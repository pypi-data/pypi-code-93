__author__ = 'yuquanfeng'

import csv
import os
from tqdm import tqdm
import torch
import datetime
import pandas as pd


def pair(size):
    return size if isinstance(size, (list, tuple)) else (size, size)


def get_img_label_from_csv(csv_file_path):
    """
    读取{csv_file_path}文件内容如下
        image, labels
        /xx/xxx/1.jpg, 0
        /xx/xxx/2.jpg, 1
    的csv文件，返回图片路径列表和标签列表
    :param csv_file_path: csv文件的路径
    """
    with open(csv_file_path) as f:
        labels = []
        imgs = []
        csv_f = csv.reader(f)
        i = 0
        for row in csv_f:
            if i == 0:
                i += 1
                continue
            imgs.append(row[0])
            labels.append(int(row[1]))
    return imgs, labels


def get_imgs_path(root, postfix=None):
    """获取root目录下的所有文件路径，若postfix不为None，则只获取指定后缀的文件,如 “.jpg”
    """
    imgs_path = []
    for root, dirs, files in os.walk(root):
        for file in files:
            if not postfix:
                imgs_path.append(os.path.join(root, file))
            elif os.path.splitext(file)[1] == postfix:  # os.path.splitext() 将文件名和扩展名分开
                imgs_path.append(os.path.join(root, file))
    return imgs_path


class Accumulator:
    """For accumulating sums over `n` variables."""

    def __init__(self, n):
        self.data = [0.0] * n

    def add(self, *args):
        self.data = [a + float(b) for a, b in zip(self.data, args)]

    def reset(self):
        self.data = [0.0] * len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


class LogTrainValid:
    """
    用于记录训练过程中的train和valid的精确率和损失值,
    并保存到csv文件中
    """

    def __init__(self):
        self.train_log = []
        self.train_acc_log = []
        self.train_loss_log = []
        self.val_acc_log = []
        self.val_loss_log = []

    def add(self, log, acc, loss, val_acc, val_loss):
        self.train_log.append(log)
        self.train_acc_log.append(acc)
        self.train_loss_log.append(loss)
        self.val_acc_log.append(val_acc)
        self.val_loss_log.append(val_loss)

    def save(self, filename):
        df = pd.DataFrame({'log': self.train_log,
                           'train_acc': self.train_acc_log,
                           'train_loss': self.train_loss_log,
                           'val_acc': self.val_acc_log,
                           'val_loss': self.val_loss_log})
        df.to_csv(filename, index=False)


class Classification:
    @staticmethod
    def train_loop(dataloader, model, loss_fn, optimizer, device):
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        model.train()
        test_loss, correct = 0, 0
        for X, y in tqdm(dataloader):
            X, y = X.to(device), y.to(device)

            # Compute prediction error
            pred = model(X)
            loss = loss_fn(pred, y)

            # save loss and correct per batch
            test_loss += loss.item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        test_loss /= num_batches
        correct /= size
        print(f"Train: \n Accuracy: {(100 * correct):>0.1f}%, Avg loss: {test_loss:>8f}")

        return test_loss, correct

    @staticmethod
    def valid_loop(dataloader, model, loss_fn, device):
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        model.eval()
        test_loss, correct = 0, 0
        with torch.no_grad():
            for X, y in tqdm(dataloader):
                X, y = X.to(device), y.to(device)
                pred = model(X)
                test_loss += loss_fn(pred, y).item()
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()
        test_loss /= num_batches
        correct /= size
        print(f"Valid: \n Accuracy: {(100 * correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

        return test_loss, correct


def get_current_time():
    now = datetime.datetime.now()
    return f'{now.year}-{now.month}-{now.day}-{now.hour}:{now.minute}'


