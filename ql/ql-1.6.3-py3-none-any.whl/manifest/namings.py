from ..scan.io import mmd
from ..fold import ns_path
from pandas import concat

__all__ = ["m", "alias_df"]

pk = ["domain", "alias"] # `labels` to name df cols and `part_keys` for attr names
cfg = {"sep": "=", "headersep": True, "labels": pk, "part_keys": pk}
m = mmd(ns_path / "alias.mmd", listparseconfig=cfg)
#aliases = {l.header.contents: [n.contents for n in l.nodes] for l in m.lists}
alias_df = {(l.header.domain, l.header.alias): l.as_df(forbid_header=True) for l in m.lists}
for k in alias_df:
    ns_long, ns_short = k
    alias_df.get(k).insert(0, "namespace", ns_short)
    alias_df.get(k).insert(0, "namespace_full", ns_long)
alias_df = concat(alias_df.values()).reset_index().drop("index", 1)
alias_df.namespace = alias_df.namespace.astype("category")
alias_df.namespace_full = alias_df.namespace_full.astype("category")
