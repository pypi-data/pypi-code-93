#!/usr/bin/env python3
"""SqueezeNet Model

This module is modified from :py:mod:`torchvision.models.squeezenet`
in order to reuse pretrained weights.
"""
from typing import Any

import megengine as mge
import megengine.functional as F
import megengine.module as M
import megengine.module.init as init
import torch


__all__ = ['SqueezeNet', 'squeezenet1_0', 'squeezenet1_1']


class Fire(M.Module):

    def __init__(
        self,
        inplanes: int,
        squeeze_planes: int,
        expand1x1_planes: int,
        expand3x3_planes: int
    ) -> None:
        super().__init__()
        self.inplanes = inplanes
        self.squeeze = M.Conv2d(inplanes, squeeze_planes, kernel_size=1)
        self.squeeze_activation = M.ReLU()
        self.expand1x1 = M.Conv2d(squeeze_planes, expand1x1_planes, kernel_size=1)
        self.expand1x1_activation = M.ReLU()
        self.expand3x3 = M.Conv2d(squeeze_planes, expand3x3_planes, kernel_size=3, padding=1)
        self.expand3x3_activation = M.ReLU()

    def forward(self, x: mge.Tensor) -> mge.Tensor:
        x = self.squeeze_activation(self.squeeze(x))
        return F.concat([
            self.expand1x1_activation(self.expand1x1(x)),
            self.expand3x3_activation(self.expand3x3(x))
        ], 1)


class SqueezeNet(M.Module):

    def __init__(
        self,
        version: str = '1_0',
        num_classes: int = 1000
    ) -> None:
        super(SqueezeNet, self).__init__()
        self.num_classes = num_classes
        if version == '1_0':
            self.features = M.Sequential(
                M.Conv2d(3, 96, kernel_size=7, stride=2),
                M.ReLU(),
                M.MaxPool2d(kernel_size=3, stride=2),
                Fire(96, 16, 64, 64),
                Fire(128, 16, 64, 64),
                Fire(128, 32, 128, 128),
                M.MaxPool2d(kernel_size=3, stride=2),
                Fire(256, 32, 128, 128),
                Fire(256, 48, 192, 192),
                Fire(384, 48, 192, 192),
                Fire(384, 64, 256, 256),
                M.MaxPool2d(kernel_size=3, stride=2),
                Fire(512, 64, 256, 256),
            )
        elif version == '1_1':
            self.features = M.Sequential(
                M.Conv2d(3, 64, kernel_size=3, stride=2),
                M.ReLU(),
                M.MaxPool2d(kernel_size=3, stride=2),
                Fire(64, 16, 64, 64),
                Fire(128, 16, 64, 64),
                M.MaxPool2d(kernel_size=3, stride=2),
                Fire(128, 32, 128, 128),
                Fire(256, 32, 128, 128),
                M.MaxPool2d(kernel_size=3, stride=2),
                Fire(256, 48, 192, 192),
                Fire(384, 48, 192, 192),
                Fire(384, 64, 256, 256),
                Fire(512, 64, 256, 256),
            )
        else:
            # FIXME: Is this needed? SqueezeNet should only be called from the
            # FIXME: squeezenet1_x() functions
            # FIXME: This checking is not done for the other models
            raise ValueError("Unsupported SqueezeNet version {version}:"
                             "1_0 or 1_1 expected".format(version=version))

        # Final convolution is initialized differently from the rest
        final_conv = M.Conv2d(512, self.num_classes, kernel_size=1)
        self.classifier = M.Sequential(
            M.Dropout(0.5),
            final_conv,
            M.ReLU(),
            M.AdaptiveAvgPool2d((1, 1))
        )

        for m in self.modules():
            if isinstance(m, M.Conv2d):
                if m is final_conv:
                    init.normal_(m.weight, mean=0.0, std=0.01)
                else:
                    init.msra_uniform_(m.weight)
                if m.bias is not None:
                    init.fill_(m.bias, 0)

    def forward(self, x: mge.Tensor) -> mge.Tensor:
        x = self.features(x)
        x = self.classifier(x)
        return F.flatten(x, 1)


def _squeezenet(version: str, pretrained: bool, progress: bool, **kwargs: Any) -> SqueezeNet:
    model = SqueezeNet(version, **kwargs)

    if pretrained:
        from torchvision.models.squeezenet import model_urls
        from torchvision.models.utils import load_state_dict_from_url

        arch = 'squeezenet' + version
        state_dict = load_state_dict_from_url(model_urls[arch], progress=progress)
        mge_sd = model.state_dict()
        for k, v in state_dict.items():
            mge_sd[k] = v.detach().numpy().reshape(mge_sd[k].shape)
        model.load_state_dict(mge_sd)

    return model


def squeezenet1_0(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> SqueezeNet:
    r"""SqueezeNet model architecture from the `"SqueezeNet: AlexNet-level
    accuracy with 50x fewer parameters and <0.5MB model size"
    <https://arxiv.org/abs/1602.07360>`_ paper.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _squeezenet('1_0', pretrained, progress, **kwargs)


def squeezenet1_1(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> SqueezeNet:
    r"""SqueezeNet 1.1 model from the `official SqueezeNet repo
    <https://github.com/DeepScale/SqueezeNet/tree/master/SqueezeNet_v1.1>`_.
    SqueezeNet 1.1 has 2.4x less computation and slightly fewer parameters
    than SqueezeNet 1.0, without sacrificing accuracy.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _squeezenet('1_1', pretrained, progress, **kwargs)


def __test():
    import numpy as np
    from torchvision import models
    model = squeezenet1_1(pretrained=True)
    model.eval()
    torch_model = models.squeezenet1_1(pretrained=True)
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
