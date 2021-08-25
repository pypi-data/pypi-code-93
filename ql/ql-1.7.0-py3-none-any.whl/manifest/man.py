from ..fold import ns_path as ss
from ..scan import mmd
from ..scan.lever.lists import SepBlockList
from .parsing import read_man

__all__ = ["ssm"]

ssm_p = ss / "manifest.mmd"
pk = ("domain", "repo_name", "priority")
sep_config = {"sep": ":", "headersep": True, "labels": None} # don't need attrs
config_dict = {"listclass": SepBlockList, "part_keys": pk, "listconfig": sep_config}
ssm = mmd(ssm_p, listparseconfig=config_dict)
ssm.repos = property(read_man).__get__(ssm)
