"""Preprocessing Factory for any Neural Networks."""
from iva_applications import lenet
from iva_applications import vgg19
from iva_applications import resnet50
from iva_applications import resnet34
from iva_applications import pnasnet
from iva_applications import squeezenet
from iva_applications import inception_v1
from iva_applications import inception_v3
from iva_applications import seresnet50
from iva_applications import densenet121
from iva_applications import efficientnet_b1
from iva_applications import efficientnet_b2
from iva_applications import efficientnet_b3
from iva_applications import efficientnet_b4
from iva_applications import efficientnet_b5
from iva_applications import covidnet_cxr4_a

PREPROCESS_FN = {
    'lenet5': lenet,
    'vgg19': vgg19,
    'resnet50': resnet50,
    'resnet50_mlperf': resnet50,
    'resnet50_v2': inception_v1,
    'resnet34': resnet34,
    'resnet152': vgg19,
    'resnext50': densenet121,
    'seresnet50': seresnet50,
    'senet154': seresnet50,
    'inception_v1': inception_v1,
    'inception_v2': inception_v1,
    'inception_v3': inception_v3,
    'inception_v4': inception_v3,
    'xception': inception_v3,
    'pnasnet_large': pnasnet,
    'pnasnet_mobile': inception_v1,
    'nasnet_mobile': inception_v1,
    'mobilenet_v1': inception_v1,
    'mobilenet_v2': inception_v1,
    'mobilenet_v1_mlperf': inception_v1,
    'squeezenet': squeezenet,
    'densenet121': inception_v1,
    'efficientnet_b0': densenet121,
    'efficientnet_b1': efficientnet_b1,
    'efficientnet_b2': efficientnet_b2,
    'efficientnet_b3': efficientnet_b3,
    'efficientnet_b4': efficientnet_b4,
    'efficientnet_b5': efficientnet_b5,
    'covidnet_cxr4_a': covidnet_cxr4_a,
}
