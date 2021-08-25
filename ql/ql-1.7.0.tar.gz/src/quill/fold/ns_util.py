from ..__share__ import ql_path
from configparser import ConfigParser
from .subdomain import parse_subdomain_url
from .distrib_setup import create_ns_aliases, create_routing_table, create_manifest
from pathlib import Path
from sys import stderr

__all__ = ["ns", "ns_path"]

def resolve_ns_path(qp=ql_path, ini_fn="spin.ini"):
    c = ConfigParser()
    with open(qp / ini_fn, "r") as f:
        c.read_file(f, ini_fn)
    rel_level = c.get("PARENT", "relative")
    dir_name = c.get("PARENT", "dir_name")
    ### This part is all about standardising whether local or distributed
    home_spin = Path.home() / "spin"
    home_is_setup = (qp / Path(*[".."]*3)).resolve() == home_spin
    if home_is_setup:
        ns_p = (qp / rel_level / dir_name).resolve()
    else:
        # this is not set up in the home directory, probably been distributed
        # if you resolve the namespace path you'll only check if the library
        # "ss" has been installed, which on PyPi is a subtitles library
        # (Don't do this! Instead set up an installation in the home directory)
        ns_p = home_spin / dir_name
        if not ns_p.exists():
            ns_p.mkdir(parents=True)
            create_ns_aliases(ns_p)
            create_routing_table(ns_p)
            create_manifest(ns_p)
    return ns_p

def read_ns(qp=ql_path, ini_fn="spin.ini"):
    ns_p = resolve_ns_path(qp, ini_fn)
    ns_subdirs = [d.name for d in ns_p.iterdir() if d.is_dir()]
    ns = {k: parse_subdomain_url(ns_p, k) for k in ns_subdirs}
    return ns

class NameSpaceDict(dict):
    def __init__(self):
        self.refresh()

    def refresh(self):
        if self != (fresh := read_ns()):
            self.clear()
            self.update(fresh)

ns = NameSpaceDict() #NameSpace()
ns_path = resolve_ns_path()
