import torch
from torch import nn
from torch.nn import functional as F
import math

class ArcSoftmax(nn.Module):
    def __init__(self, feature_num, num_classes, s=10, m=0.5, easy_margin=False):
        super(ArcSoftmax, self).__init__()
        self.easy_margin = easy_margin
        self.s = s
        self.m = m

        self.cos_m = math.cos(m)
        self.sin_m = math.sin(m)
        self.th = math.cos(math.pi - m)
        self.mm = math.sin(math.pi - m) * m

        self.weight = nn.Parameter(torch.Tensor(num_classes, feature_num), requires_grad=True)
        nn.init.xavier_normal_(self.weight)

    def forward(self, x):
        _x = F.normalize(x, p=2, dim=1)
        _w = F.normalize(self.weight, p=2, dim=1)
        cosine = F.linear(_x, _w, bias=None)

        # softmax
        if self.training:
            sine = torch.sqrt((1.0 - torch.pow(cosine, 2)).clamp(0, 1))
            phi = cosine * self.cos_m - sine * self.sin_m
            # keep monotonicity of loss function
            if self.easy_margin:
                phi = torch.where(cosine > 0, phi, cosine)
            else:
                phi = torch.where(cosine > self.th, phi, cosine - self.mm)

            numerator = torch.exp(phi * self.s)
            denominator = torch.exp(cosine * self.s)
            denominator = torch.sum(denominator, dim=1, keepdim=True) - denominator + numerator
            return numerator / denominator
        else:
            numerator = torch.exp(cosine * self.s)
            denominator = torch.sum(numerator, dim=1, keepdim=True)
            return numerator / denominator

if __name__ == '__main__':
    arc_softmax = ArcSoftmax(128, 3, 10, 0.5)

    inputs = torch.rand((3, 128), dtype=torch.float)
    arc_softmax.train()
    outputs = arc_softmax(inputs)
    print(outputs)

    arc_softmax.eval()
    outputs = arc_softmax(inputs)
    print(outputs)
