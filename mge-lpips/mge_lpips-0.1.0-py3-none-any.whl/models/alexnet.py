#!/usr/bin/env python3
"""AlexNet Model

This module is modified from :py:mod:`torchvision.models.alexnet`
in order to reuse pretrained weights.
"""
from typing import Any
import megengine as mge
import megengine.functional as F
import megengine.module as M
import torch

__all__ = ['AlexNet', 'alexnet']


class AlexNet(M.Module):

    def __init__(self, num_classes: int = 1000) -> None:
        super().__init__()
        self.features = M.Sequential(
            M.Conv2d(3, 64, kernel_size=11, stride=4, padding=2),
            M.ReLU(),
            M.MaxPool2d(kernel_size=3, stride=2),
            M.Conv2d(64, 192, kernel_size=5, padding=2),
            M.ReLU(),
            M.MaxPool2d(kernel_size=3, stride=2),
            M.Conv2d(192, 384, kernel_size=3, padding=1),
            M.ReLU(),
            M.Conv2d(384, 256, kernel_size=3, padding=1),
            M.ReLU(),
            M.Conv2d(256, 256, kernel_size=3, padding=1),
            M.ReLU(),
            M.MaxPool2d(kernel_size=3, stride=2),
        )
        self.avgpool = M.AdaptiveAvgPool2d((6, 6))
        self.classifier = M.Sequential(
            M.Dropout(),
            M.Linear(256 * 6 * 6, 4096),
            M.ReLU(),
            M.Dropout(),
            M.Linear(4096, 4096),
            M.ReLU(),
            M.Linear(4096, num_classes),
        )

    def forward(self, x: mge.Tensor) -> mge.Tensor:
        x = self.features(x)
        x = self.avgpool(x)
        x = F.flatten(x, 1)
        x = self.classifier(x)
        return x


def alexnet(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> AlexNet:
    r"""AlexNet model architecture from the
    `"One weird trick..." <https://arxiv.org/abs/1404.5997>`_ paper.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    model = AlexNet(**kwargs)
    if pretrained:
        from torchvision.models.alexnet import model_urls
        from torchvision.models.utils import load_state_dict_from_url

        state_dict = load_state_dict_from_url(model_urls['alexnet'], progress=progress)
        mge_sd = model.state_dict()
        for k, v in state_dict.items():
            mge_sd[k] = v.detach().numpy().reshape(mge_sd[k].shape)
        model.load_state_dict(mge_sd)

    return model


def __test():
    import numpy as np
    from torchvision import models

    model = alexnet(pretrained=True)
    model.eval()
    torch_model = models.alexnet(pretrained=True)
    torch_model.eval()

    in_ten = np.random.uniform(0, 1, size=(1, 3, 256, 256)).astype(np.float32)

    mge_out = model(mge.tensor(in_ten))
    torch_out = torch_model(torch.from_numpy(in_ten)).detach().numpy()
    print(mge_out.shape)
    print(torch_out.shape)
    diff = np.abs(mge_out - torch_out)
    print(diff.max(), diff.mean())


if __name__ == '__main__':
    __test()
