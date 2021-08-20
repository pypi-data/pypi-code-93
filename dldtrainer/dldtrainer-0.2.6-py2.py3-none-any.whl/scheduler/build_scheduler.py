# -*-coding: utf-8 -*-
"""
    @Author : panjq
    @E-mail : pan_jinquan@163.com
    @Date   : 2021-08-12 20:31:19
"""
from .MultiStepLR import MultiStepLR
from .CosineAnnealingLR import CosineAnnealingLR


def get_scheduler(scheduler, optimizer, lr_init, num_epochs, num_steps, **kwargs):
    if scheduler == "multi-step" or scheduler == "multi_step":
        lr_scheduler = MultiStepLR(optimizer,
                                   lr_init=lr_init,
                                   epochs=num_epochs,
                                   num_steps=num_steps,
                                   milestones=kwargs["milestones"],
                                   num_warn_up=kwargs["num_warn_up"])
    elif scheduler == "cosine":
        # 余弦退火学习率调整策略
        lr_scheduler = CosineAnnealingLR(optimizer,
                                         num_epochs,
                                         num_steps=num_steps,
                                         lr_init=lr_init,
                                         num_warn_up=kwargs["num_warn_up"]
                                         )
    else:
        raise Exception("Error: scheduler type: {}".format(scheduler))
    return lr_scheduler
