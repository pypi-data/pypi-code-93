# -*-coding: utf-8 -*-
"""
    @Author : panjq
    @E-mail : pan_jinquan@163.com
    @Date   : 2021-08-12 20:27:27
"""

import torch
import torch.optim as optim
import torch.nn as nn
import numpy as np
from ..callbacks.callbacks import Callback
from .WarmUpLR import WarmUpLR
from torch.optim import lr_scheduler


class CosineAnnealingLR(Callback):
    def __init__(self,
                 optimizer,
                 epochs,
                 num_steps,
                 lr_init=0.1,
                 num_warn_up=0,
                 ):
        """
        余弦退火学习率调整策略
        optimizer (Optimizer): Wrapped optimizer.
        t_max (int): Maximum number of iterations.
        eta_min (float): Minimum learning rate. Default: 0.
        last_epoch (int): The index of last epoch. Default: -1.
        verbose (bool): If ``True``, prints a message to stdout for each update. Default: ``False``.
        """
        super(CosineAnnealingLR, self).__init__()
        self.num_steps = num_steps
        self.epoch = 0
        t_max = epochs * 1.0  # 一次学习率周期的迭代次数，即 T_max 个 epoch 之后重新设置学习率。
        eta_min = 0.00000  # 最小学习率，即在一个周期中，学习率最小会下降到 eta_min，默认值为 0
        self.scheduler = lr_scheduler.CosineAnnealingLR(optimizer, t_max, eta_min=eta_min, last_epoch=-1, verbose=False)
        self.warm_up = WarmUpLR(optimizer,
                                num_steps=self.num_steps,
                                lr_init=lr_init,
                                num_warn_up=num_warn_up)

    def on_epoch_begin(self, epoch, logs: dict = {}):
        self.epoch = epoch

    def on_batch_end(self, batch, logs: dict = {}):
        self.step(epoch=self.epoch, step=batch)

    def step(self, epoch=0, step=0):
        # total_step = self.num_steps * epoch + step
        self.scheduler.step(epoch)
        self.warm_up.step(epoch, step)
