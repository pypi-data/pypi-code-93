from collections import OrderedDict

import torch
from torchvision import models

from ftools.GLOBAL_LOG import flog
from ftools.ai.fmodels.f_layer_get import ModelOuts4Resnet


class Net3(torch.nn.Module):
    def __init__(self):
        super(Net3, self).__init__()
        self.conv1 = torch.nn.Sequential()
        self.conv1.add_module("conv1", torch.nn.Conv2d(3, 32, 3, 1, 1))
        self.conv1.add_module("relu1", torch.nn.ReLU())
        self.conv1.add_module("pool1", torch.nn.MaxPool2d(2))

        self.conv2 = torch.nn.Conv2d(3, 32, 3, 1, 1)

        self.dense1 = torch.nn.Sequential()
        self.dense1.add_module("dense1", torch.nn.Linear(32 * 3 * 3, 128))
        self.dense1.add_module("relu2", torch.nn.ReLU())
        self.dense1.add_module("dense2", torch.nn.Linear(128, 10))

        self.dense2 = torch.nn.Sequential(
            torch.nn.Linear(32 * 3 * 3, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 10)
        )

        self.conv3 = torch.nn.Sequential(
            OrderedDict(
                [
                    ("conv1", torch.nn.Conv2d(3, 32, 3, 1, 1)),
                    ("relu1", torch.nn.ReLU()),
                    ("pool1", torch.nn.MaxPool2d(2))
                ]
            ))

    def forward(self, x):
        conv_out = self.conv1(x)
        res = conv_out.view(conv_out.size(0), -1)
        out = self.dense(res)
        return out


def f1(model_children):
    '''
    后序遍历
    for module in self.children():
            module.apply(fn)
        fn(self)
        return self
    :param model_children:
    :return:
    '''
    pass


if __name__ == '__main__':
    '''
    t开头为测试文件
    '''
    model = models.resnet50(pretrained=True)
    dims_out = (512, 1024, 2048)
    model = ModelOuts4Resnet(model, dims_out)

    # for i, (name, param) in enumerate(model.named_parameters()):
    #     # 深度优化钻取
    #     print('---------- %s ----------' % i,
    #           'name =', name,
    #           '      ', param.shape)

    for i, (name, child) in enumerate(model.named_children()):
        # 这个不能钻取  获取的是下一级的 nn.Module  例如name <class 'torchvision.models.resnet.ResNet'>
        print('---------- %s ----------' % i)
        flog.debug('name %s', name)
        print(child)

    # for i, c in enumerate(model.children()):
    #     # 这个不能钻取
    #     print('---------- %s ----------' % i)
    #     print(c)

    # for i, m in enumerate(model.modules()):
    for i, (name, m) in enumerate(model.named_modules()):
        # 深度优先 这个是钻取 nn.Module <class 'f_pytorch.tools_model.f_layer_get.ModelOuts4Resnet'>
        print('---------- %s ----------' % i)
        pass

    for i, p in enumerate(model.parameters()):
        # 遍历出每一个参数 p这个是自定钻取
        print('---------- %s ----------' % i)
        pass

    model.apply(f1)  # 不重复递归
