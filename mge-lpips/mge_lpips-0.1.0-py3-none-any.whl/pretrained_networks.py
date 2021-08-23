#!/usr/bin/env python3
from collections import namedtuple, OrderedDict

import megengine as mge
import megengine.module as M
import megengine.functional as F
import megengine.module.init as init
import torch

from . import models


class SqueezeNet(M.Module):

    def __init__(self, pretrained=True):
        super().__init__()
        pretrained_features = models.squeezenet1_1(pretrained=pretrained).features
        self.slice1 = OrderedDict()
        self.slice2 = OrderedDict()
        self.slice3 = OrderedDict()
        self.slice4 = OrderedDict()
        self.slice5 = OrderedDict()
        self.slice6 = OrderedDict()
        self.slice7 = OrderedDict()
        self.N_slices = 7
        for x in range(2):
            self.slice1[str(x)] = pretrained_features[x]
        for x in range(2, 5):
            self.slice2[str(x)] = pretrained_features[x]
        for x in range(5, 8):
            self.slice3[str(x)] = pretrained_features[x]
        for x in range(8, 10):
            self.slice4[str(x)] = pretrained_features[x]
        for x in range(10, 11):
            self.slice5[str(x)] = pretrained_features[x]
        for x in range(11, 12):
            self.slice6[str(x)] = pretrained_features[x]
        for x in range(12, 13):
            self.slice7[str(x)] = pretrained_features[x]

        self.slice1 = M.Sequential(self.slice1)
        self.slice2 = M.Sequential(self.slice2)
        self.slice3 = M.Sequential(self.slice3)
        self.slice4 = M.Sequential(self.slice4)
        self.slice5 = M.Sequential(self.slice5)
        self.slice6 = M.Sequential(self.slice6)
        self.slice7 = M.Sequential(self.slice7)

    def forward(self, X: mge.Tensor):
        h = self.slice1(X)
        h_relu1 = h
        h = self.slice2(h)
        h_relu2 = h
        h = self.slice3(h)
        h_relu3 = h
        h = self.slice4(h)
        h_relu4 = h
        h = self.slice5(h)
        h_relu5 = h
        h = self.slice6(h)
        h_relu6 = h
        h = self.slice7(h)
        h_relu7 = h
        squeeze_outputs = namedtuple(
            "SqueezeOutputs",
            ['relu1', 'relu2', 'relu3', 'relu4', 'relu5', 'relu6', 'relu7'],
        )
        out = squeeze_outputs(h_relu1, h_relu2, h_relu3, h_relu4, h_relu5, h_relu6, h_relu7)

        return out


class AlexNet(M.Module):

    def __init__(self, pretrained=True):
        super().__init__()
        alexnet_pretrained_features = models.alexnet(pretrained=pretrained).features
        self.slice1 = OrderedDict()
        self.slice2 = OrderedDict()
        self.slice3 = OrderedDict()
        self.slice4 = OrderedDict()
        self.slice5 = OrderedDict()
        self.N_slices = 5
        for x in range(2):
            self.slice1[str(x)] = alexnet_pretrained_features[x]
        for x in range(2, 5):
            self.slice2[str(x)] = alexnet_pretrained_features[x]
        for x in range(5, 8):
            self.slice3[str(x)] = alexnet_pretrained_features[x]
        for x in range(8, 10):
            self.slice4[str(x)] = alexnet_pretrained_features[x]
        for x in range(10, 12):
            self.slice5[str(x)] = alexnet_pretrained_features[x]

        self.slice1 = M.Sequential(self.slice1)
        self.slice2 = M.Sequential(self.slice2)
        self.slice3 = M.Sequential(self.slice3)
        self.slice4 = M.Sequential(self.slice4)
        self.slice5 = M.Sequential(self.slice5)

    def forward(self, X):
        h = self.slice1(X)
        h_relu1 = h
        h = self.slice2(h)
        h_relu2 = h
        h = self.slice3(h)
        h_relu3 = h
        h = self.slice4(h)
        h_relu4 = h
        h = self.slice5(h)
        h_relu5 = h
        alexnet_outputs = namedtuple("AlexnetOutputs", ['relu1', 'relu2', 'relu3', 'relu4', 'relu5'])
        out = alexnet_outputs(h_relu1, h_relu2, h_relu3, h_relu4, h_relu5)

        return out


class VGG16(M.Module):
    def __init__(self, pretrained=True):
        super().__init__()
        vgg_pretrained_features = models.vgg16(pretrained=pretrained).features
        self.slice1 = OrderedDict()
        self.slice2 = OrderedDict()
        self.slice3 = OrderedDict()
        self.slice4 = OrderedDict()
        self.slice5 = OrderedDict()
        self.N_slices = 5
        for x in range(4):
            self.slice1[str(x)] = vgg_pretrained_features[x]
        for x in range(4, 9):
            self.slice2[str(x)] = vgg_pretrained_features[x]
        for x in range(9, 16):
            self.slice3[str(x)] = vgg_pretrained_features[x]
        for x in range(16, 23):
            self.slice4[str(x)] = vgg_pretrained_features[x]
        for x in range(23, 30):
            self.slice5[str(x)] = vgg_pretrained_features[x]
        self.slice1 = M.Sequential(self.slice1)
        self.slice2 = M.Sequential(self.slice2)
        self.slice3 = M.Sequential(self.slice3)
        self.slice4 = M.Sequential(self.slice4)
        self.slice5 = M.Sequential(self.slice5)

    def forward(self, X):
        h = self.slice1(X)
        h_relu1_2 = h
        h = self.slice2(h)
        h_relu2_2 = h
        h = self.slice3(h)
        h_relu3_3 = h
        h = self.slice4(h)
        h_relu4_3 = h
        h = self.slice5(h)
        h_relu5_3 = h
        vgg_outputs = namedtuple("VggOutputs", ['relu1_2', 'relu2_2', 'relu3_3', 'relu4_3', 'relu5_3'])
        out = vgg_outputs(h_relu1_2, h_relu2_2, h_relu3_3, h_relu4_3, h_relu5_3)

        return out
