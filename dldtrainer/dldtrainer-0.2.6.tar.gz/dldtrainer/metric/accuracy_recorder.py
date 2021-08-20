# -*-coding: utf-8 -*-
"""
    @Author : panjq
    @E-mail : pan_jinquan@163.com
    @Date   : 2021-07-28 11:32:42
"""
import numpy as np
import torch
from sklearn.metrics import accuracy_score
from .eval_tools.metrics import AverageMeter, accuracy
from ..callbacks import callbacks
from .eval_tools import classification_report
from ..utils import log, file_utils


class AccuracyRecorder(callbacks.Callback):
    def __init__(self, target_names=None, indicator="Acc"):
        """
        计算Accuracy的回调函数
        :param target_names: list of str of shape (n_labels,), default=None
                             Optional display names matching the labels (same order).
        :param indicator: 指标名称
        """
        super(AccuracyRecorder, self).__init__()
        self.target_names = target_names
        self.indicator = indicator
        self.train_top1 = AverageMeter()
        self.test_top1 = AverageMeter()
        self.true_labels = np.ones(0)
        self.pred_labels = np.ones(0)
        self.logger = log.get_logger()


    def on_epoch_begin(self, epoch, logs: dict = {}):
        self.train_top1.reset()

    def on_test_begin(self, logs: dict = {}):
        self.test_top1.reset()
        self.true_labels = np.ones(0)
        self.pred_labels = np.ones(0)

    def on_test_end(self, logs: dict = {}):
        acc = accuracy_score(self.true_labels, self.pred_labels) * 100.0
        report = classification_report.get_classification_report(self.true_labels,
                                                                 self.pred_labels,
                                                                 target_names=self.target_names)
        # confuse_file = os.path.join(self.log_root, "confusion_matrix.csv")
        # conf_matrix = classification_report.get_confusion_matrix(true_labels, pred_labels, None, confuse_file)
        self.logger.info("\nAcc:{:.4f}\n{}".format(acc, report))

    @staticmethod
    def summary(phase, average_meter: AverageMeter, indicator, inputs, outputs, logs: dict = {}):
        targets, labels = inputs
        acc, = accuracy(outputs.data, labels, topk=(1,))
        # fix a bug: n = labels.size(0)
        average_meter.update(acc.data.item(), labels.size(0))
        logs[phase] = logs[phase] if phase in logs else {}
        logs[phase][indicator] = average_meter.avg

    def on_train_summary(self, inputs, outputs, losses, epoch, step, logs: dict = {}):
        # measure accuracy
        self.summary(phase="train", average_meter=self.train_top1, indicator=self.indicator,
                     inputs=inputs, outputs=outputs, logs=logs)

    def on_test_summary(self, inputs, outputs, losses, epoch, batch, logs: dict = {}):
        # measure accuracy
        targets, labels = inputs
        self.summary(phase="test", average_meter=self.test_top1, indicator=self.indicator,
                     inputs=inputs, outputs=outputs, logs=logs)
        # get predict result
        outputs = torch.nn.functional.softmax(outputs, dim=1)
        pred_score, pred_index = torch.max(outputs, dim=1)
        pred_index = pred_index.cpu().detach().numpy()
        labels = labels.cpu().detach().numpy()
        self.true_labels = np.hstack([self.true_labels, labels])
        self.pred_labels = np.hstack([self.pred_labels, pred_index])
