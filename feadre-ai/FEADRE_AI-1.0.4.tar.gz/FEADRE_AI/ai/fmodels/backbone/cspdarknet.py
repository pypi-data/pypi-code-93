import torch
from torch import nn

from ftools.ai.fmodels.backbone.net_blocks import BaseConv, Bottleneck, DWConv, SPPBottleneck


class CSPLayer(nn.Module):
    """C3 in yolov5, CSP Bottleneck with 3 convolutions"""

    def __init__(
            self, in_channels, out_channels, n=1,
            shortcut=True, expansion=0.5, depthwise=False, act="silu"
    ):
        """
        Args:
            in_channels (int): input channels.
            out_channels (int): output channels.
            n (int): number of Bottlenecks. Default value: 1.
        """
        # ch_in, ch_out, number, shortcut, groups, expansion
        super().__init__()
        hidden_channels = int(out_channels * expansion)  # hidden channels
        self.conv1 = BaseConv(in_channels, hidden_channels, 1, stride=1, act=act)
        self.conv2 = BaseConv(in_channels, hidden_channels, 1, stride=1, act=act)
        self.conv3 = BaseConv(2 * hidden_channels, out_channels, 1, stride=1, act=act)
        module_list = [
            Bottleneck(hidden_channels, hidden_channels, shortcut, 1.0, depthwise, act=act)
            for _ in range(n)
        ]
        self.m = nn.Sequential(*module_list)

    def forward(self, x):
        x_1 = self.conv1(x)
        x_2 = self.conv2(x)
        x_1 = self.m(x_1)
        x = torch.cat((x_1, x_2), dim=1)
        return self.conv3(x)


class Focus(nn.Module):
    """Focus width and height information into channel space."""

    def __init__(self, in_channels, out_channels, ksize=1, stride=1, act="silu"):
        super().__init__()
        self.conv = BaseConv(in_channels * 4, out_channels, ksize, stride, act=act)

    def forward(self, x):
        # shape of x (b,c,w,h) -> y(b,4c,w/2,h/2)
        # patch_top_left = x[..., ::2, ::2]
        # patch_top_right = x[..., ::2, 1::2]
        # patch_bot_left = x[..., 1::2, ::2]
        # patch_bot_right = x[..., 1::2, 1::2]

        j02_2 = torch.arange(0, x.shape[2], 2)
        j12_2 = torch.arange(1, x.shape[2], 2)
        j02_3 = torch.arange(0, x.shape[3], 2)
        j12_3 = torch.arange(1, x.shape[3], 2)
        patch_top_left = x[..., j02_2, :][..., j02_3]
        patch_top_right = x[..., j02_2, :][..., j12_3]
        patch_bot_left = x[..., j12_2, :][..., j02_3]
        patch_bot_right = x[..., j12_2, :][..., j12_3]

        x = torch.cat(
            (patch_top_left, patch_bot_left, patch_top_right, patch_bot_right,), dim=1,
        )
        return self.conv(x)


class CSPDarknet(nn.Module):

    def __init__(self, dep_mul, wid_mul,
                 out_features=("dark3", "dark4", "dark5"),
                 depthwise=False, act="silu",
                 ):
        super().__init__()
        assert out_features, "please provide output features of Darknet"
        self.out_features = out_features
        Conv = DWConv if depthwise else BaseConv

        base_channels = int(wid_mul * 64)  # 64
        base_depth = max(round(dep_mul * 3), 1)  # 3

        # stem
        self.stem = Focus(3, base_channels, ksize=3, act=act)

        # dark2
        self.dark2 = nn.Sequential(
            Conv(base_channels, base_channels * 2, 3, 2, act=act),
            CSPLayer(
                base_channels * 2, base_channels * 2,
                n=base_depth, depthwise=depthwise, act=act
            ),
        )

        # dark3
        self.dark3 = nn.Sequential(
            Conv(base_channels * 2, base_channels * 4, 3, 2, act=act),
            CSPLayer(
                base_channels * 4, base_channels * 4,
                n=base_depth * 3, depthwise=depthwise, act=act,
            ),
        )

        # dark4
        self.dark4 = nn.Sequential(
            Conv(base_channels * 4, base_channels * 8, 3, 2, act=act),
            CSPLayer(
                base_channels * 8, base_channels * 8,
                n=base_depth * 3, depthwise=depthwise, act=act,
            ),
        )

        # dark5
        self.dark5 = nn.Sequential(
            Conv(base_channels * 8, base_channels * 16, 3, 2, act=act),
            SPPBottleneck(base_channels * 16, base_channels * 16, activation=act),
            CSPLayer(
                base_channels * 16, base_channels * 16, n=base_depth,
                shortcut=False, depthwise=depthwise, act=act,
            ),
        )

    def forward(self, x):
        outputs = {}
        x = self.stem(x)
        outputs["stem"] = x
        x = self.dark2(x)
        outputs["dark2"] = x
        x = self.dark3(x)
        outputs["dark3"] = x
        x = self.dark4(x)
        outputs["dark4"] = x
        x = self.dark5(x)
        outputs["dark5"] = x

        outs_dict = {k: v for k, v in outputs.items() if k in self.out_features}
        return list(outs_dict.values())
        # return outputs["dark3"], outputs["dark4"], outputs["dark5"]


class YOLOXFPN(nn.Module):
    def __init__(self, in_channels, depth=1.0, width=1.0, ):
        super().__init__()
        act = "silu"
        self.upsample = nn.Upsample(scale_factor=2, mode="nearest")
        self.lateral_conv0 = BaseConv(
            int(in_channels[2] * width), int(in_channels[1] * width), 1, 1, act=act
        )

    def forward(self, input):
        pass


if __name__ == '__main__':
    pass
