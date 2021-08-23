#!/usr/bin/env python3
import megengine as mge
import megengine.module as M
import megengine.functional as F
import megengine.module.init as init
import numpy as np
import torch

from . import pretrained_networks as pn
from .utils import NetName, LPIPS_VER, pretrained_weight


def normalize_tensor(in_feat, eps=1e-10):
    norm_factor = F.sqrt(F.sum(in_feat**2, axis=1, keepdims=True))
    return in_feat/(norm_factor+eps)


class LPIPS(M.Module):
    # Learned perceptual metric

    def __init__(
        self, net: NetName = 'alex', version: LPIPS_VER = '0.1',
        pretrained=True, model_path=None, verbose=True
    ):
        super().__init__()

        self.version = version

        self.scaling_layer = ScalingLayer()

        if net == "vgg16":
            NetClass = pn.VGG16
            self.chns = [64, 128, 256, 512, 512]
        elif net == "alex":
            NetClass = pn.AlexNet
            self.chns = [64, 192, 384, 256, 256]
        elif net == "squeeze":
            NetClass = pn.SqueezeNet
            self.chns = [64, 128, 256, 384, 384, 512, 512]

        self.lins = [
            M.Conv2d(chn, out_channels=1, kernel_size=1, stride=1, padding=0, bias=False)
            for chn in self.chns
        ]

        if pretrained:
            if model_path is None:
                model_path = pretrained_weight(net, self.version)

            if verbose:
                print("[LPIPS] loading pretrained weights:", model_path)

            torch_sd = torch.load(model_path, map_location=torch.device('cpu'))
            mge_sd = self.state_dict()
            for k, v in torch_sd.items():
                # lin0.model.1.weight -> lins.0.weight
                lin_id = k.split('.')[0][len('lin'):]
                mk = "lins.{}.weight".format(lin_id)
                mge_sd[mk] = v.detach().cpu().numpy().reshape(mge_sd[mk].shape)
            self.load_state_dict(mge_sd)

        self.backbone = NetClass(pretrained=pretrained)
        self.eval()

    def forward(self, in0, in1, retPerLayer=False):
        # v0.0 - original release had a bug, where input was not scaled
        in0_input, in1_input = (self.scaling_layer(in0), self.scaling_layer(in1)) if self.version == '0.1' else (in0, in1)
        outs0, outs1 = self.backbone.forward(in0_input), self.backbone.forward(in1_input)

        res = []
        for out0, out1, lin in zip(outs0, outs1, self.lins):
            feats0, feats1 = normalize_tensor(out0), normalize_tensor(out1)
            ldiff = lin((feats0 - feats1) ** 2)
            res.append(ldiff.mean(axis=[2, 3], keepdims=True))

        val = sum(res)

        if retPerLayer:
            return (val, res)
        else:
            return val


class ScalingLayer(M.Module):

    def __init__(self):
        super().__init__()
        self.shift = mge.Tensor([-.030, -.088, -.188]).reshape(1, 3, 1, 1)
        self.scale = mge.Tensor([.458, .448, .450]).reshape(1, 3, 1, 1)

    def forward(self, inp):
        return (inp - self.shift) / self.scale