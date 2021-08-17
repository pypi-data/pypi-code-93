# -*-coding: utf-8 -*-
"""
    @Author : panjq
    @E-mail : pan_jinquan@163.com
    @Date   : 2021-07-19 14:19:35
"""

import torch.optim as optim


def get_optimizer(model, optim_type="SGD", **kwargs):
    """
    :param optim_type:
    :return:
    """
    # params = filter(lambda p: p.requires_grad, self.model.parameters())
    params = model.parameters()
    if optim_type == "SGD":
        optimizer = optim.SGD(params,
                              lr=kwargs["lr"],
                              momentum=kwargs["momentum"],
                              weight_decay=kwargs["weight_decay"])
    elif optim_type == "Adam":
        # β1和β2是加权平均数,用于控制一阶动量和二阶动量
        optimizer = optim.Adam(params,
                               lr=kwargs["lr"],
                               weight_decay=kwargs["weight_decay"])
    elif optim_type == "AdamW":
        optimizer = optim.AdamW(params,
                                lr=kwargs["lr"],
                                weight_decay=kwargs["weight_decay"])
    else:
        raise Exception("Error:{}".format(optim_type))
    return optimizer
