from .yacs.config import CfgNode as CN
import os

def yacsConfig(yaml):
    assert os.path.exists(yaml), "not exists:{}".format(yaml)
    with open(yaml, 'r') as f:
        cfg = CN.load_cfg(f)
        cfg.freeze()
    return cfg

