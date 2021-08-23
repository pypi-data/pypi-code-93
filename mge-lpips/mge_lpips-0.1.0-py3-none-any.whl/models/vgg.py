#!/usr/bin/env python3
"""VGG Model

This module is modified from :py:mod:`torchvision.models.vgg`
in order to reuse pretrained weights.
"""
from typing import Union, List, Dict, Any, cast

import megengine as mge
import megengine.module as M
import megengine.functional as F
import megengine.module.init as init
import torch

__all__ = ['VGG', 'vgg16']


class VGG(M.Module):

    def __init__(
        self,
        features: M.Module,
        num_classes: int = 1000,
        init_weights: bool = True
    ) -> None:
        super().__init__()
        self.features = features
        self.avgpool = M.AdaptiveAvgPool2d((7, 7))
        self.classifier = M.Sequential(
            M.Linear(512 * 7 * 7, 4096),
            M.ReLU(),
            M.Dropout(),
            M.Linear(4096, 4096),
            M.ReLU(),
            M.Dropout(),
            M.Linear(4096, num_classes),
        )
        if init_weights:
            self._initialize_weights()

    def forward(self, x: mge.Tensor) -> mge.Tensor:
        x = self.features(x)
        x = self.avgpool(x)
        x = F.flatten(x, 1)
        x = self.classifier(x)
        return x

    def _initialize_weights(self) -> None:
        for m in self.modules():
            if isinstance(m, M.Conv2d):
                init.msra_normal_(m.weight, mode='fan_out', nonlinearity='relu')

                if m.bias is not None:
                    init.fill_(m.bias, 0.0)

            elif isinstance(m, M.BatchNorm2d):
                init.fill_(m.weight, 1)
                init.fill_(m.bias, 0)
            elif isinstance(m, M.Linear):
                init.normal_(m.weight, 0, 0.01)
                init.fill_(m.bias, 0)


def make_layers(cfg: List[Union[str, int]], batch_norm: bool = False) -> M.Sequential:
    layers: List[M.Module] = []
    in_channels = 3
    for v in cfg:
        if v == 'M':
            layers += [M.MaxPool2d(kernel_size=2, stride=2)]
        else:
            v = cast(int, v)
            conv2d = M.Conv2d(in_channels, v, kernel_size=3, padding=1)
            if batch_norm:
                layers += [conv2d, M.BatchNorm2d(v), M.ReLU()]
            else:
                layers += [conv2d, M.ReLU()]
            in_channels = v
    return M.Sequential(*layers)


cfgs: Dict[str, List[Union[str, int]]] = {
    'A': [64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
    'B': [64, 64, 'M', 128, 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
    'D': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'],
    'E': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 256, 'M', 512, 512, 512, 512, 'M', 512, 512, 512, 512, 'M'],
}


def _vgg(arch: str, cfg: str, batch_norm: bool, pretrained: bool, progress: bool, **kwargs: Any) -> VGG:
    if pretrained:
        kwargs['init_weights'] = False
    model = VGG(make_layers(cfgs[cfg], batch_norm=batch_norm), **kwargs)
    if pretrained:
        from torchvision.models.vgg import model_urls
        from torchvision.models.utils import load_state_dict_from_url
        state_dict = load_state_dict_from_url(model_urls[arch], progress=progress)
        mge_sd = model.state_dict()
        for k, v in state_dict.items():
            mge_sd[k] = v.detach().numpy().reshape(mge_sd[k].shape)
        model.load_state_dict(mge_sd)
    return model


def vgg11(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> VGG:
    r"""VGG 11-layer model (configuration "A") from
    `"Very Deep Convolutional Networks For Large-Scale Image Recognition" <https://arxiv.org/pdf/1409.1556.pdf>`._
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _vgg('vgg11', 'A', False, pretrained, progress, **kwargs)


def vgg11_bn(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> VGG:
    r"""VGG 11-layer model (configuration "A") with batch normalization
    `"Very Deep Convolutional Networks For Large-Scale Image Recognition" <https://arxiv.org/pdf/1409.1556.pdf>`._
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _vgg('vgg11_bn', 'A', True, pretrained, progress, **kwargs)


def vgg13(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> VGG:
    r"""VGG 13-layer model (configuration "B")
    `"Very Deep Convolutional Networks For Large-Scale Image Recognition" <https://arxiv.org/pdf/1409.1556.pdf>`._
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _vgg('vgg13', 'B', False, pretrained, progress, **kwargs)


def vgg13_bn(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> VGG:
    r"""VGG 13-layer model (configuration "B") with batch normalization
    `"Very Deep Convolutional Networks For Large-Scale Image Recognition" <https://arxiv.org/pdf/1409.1556.pdf>`._
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _vgg('vgg13_bn', 'B', True, pretrained, progress, **kwargs)


def vgg16(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> VGG:
    r"""VGG 16-layer model (configuration "D")
    `"Very Deep Convolutional Networks For Large-Scale Image Recognition" <https://arxiv.org/pdf/1409.1556.pdf>`._
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _vgg('vgg16', 'D', False, pretrained, progress, **kwargs)


def vgg16_bn(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> VGG:
    r"""VGG 16-layer model (configuration "D") with batch normalization
    `"Very Deep Convolutional Networks For Large-Scale Image Recognition" <https://arxiv.org/pdf/1409.1556.pdf>`._
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _vgg('vgg16_bn', 'D', True, pretrained, progress, **kwargs)


def vgg19(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> VGG:
    r"""VGG 19-layer model (configuration "E")
    `"Very Deep Convolutional Networks For Large-Scale Image Recognition" <https://arxiv.org/pdf/1409.1556.pdf>`._
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _vgg('vgg19', 'E', False, pretrained, progress, **kwargs)


def vgg19_bn(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> VGG:
    r"""VGG 19-layer model (configuration 'E') with batch normalization
    `"Very Deep Convolutional Networks For Large-Scale Image Recognition" <https://arxiv.org/pdf/1409.1556.pdf>`._
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _vgg('vgg19_bn', 'E', True, pretrained, progress, **kwargs)


def __test():
    import numpy as np
    from torchvision import models
    model = vgg16(pretrained=True)
    model.eval()
    torch_model = models.vgg16(pretrained=True)
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
