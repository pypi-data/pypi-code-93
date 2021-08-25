from ...fold import ns_path
from ...manifest.namings import alias_df
from ..io import mmd
from pandas import concat

__all__ = ["routing_df"]

assert (routing_mmd := ns_path / "routing.mmd").exists(), f"No file {routing_mmd=}"

pk = ["domain", "route"] # route is 'dev' or 'local' relative filesystem path
cfg = {"sep": "=", "headersep": False, "labels": pk, "part_keys": pk}
r = mmd(routing_mmd, listparseconfig=cfg)
routing_df = {l.header.contents: l.as_df(forbid_header=True) for l in r.lists}
for routing_ns in routing_df:
    routing_df.get(routing_ns).insert(0, "namespace_full", routing_ns)
routing_df = concat([routing_df.get(ns) for ns in routing_df]).reset_index().drop("index", 1)
routing_df.namespace_full = routing_df.namespace_full.astype("category")
routing_df = alias_df.merge(routing_df, on=["namespace_full","domain"])
