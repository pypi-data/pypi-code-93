#!/usr/bin/env python3
from pathlib import Path
from typing import Union
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


LPIPS_VER = Union[Literal["0.0"], Literal["0.1"]]
NetName = Union[Literal["alexnet"], Literal["alexnet"], Literal["alexnet"]]


def pretrained_weight(netname: NetName, version: LPIPS_VER = "0.1") -> Path:
    return Path(__file__).with_name("weights") / ("v"+version) / (netname+'.pth')
