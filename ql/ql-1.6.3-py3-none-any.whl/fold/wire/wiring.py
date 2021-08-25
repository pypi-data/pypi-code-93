from configparser import ConfigParser
from pathlib import Path
from ..ns_util import ns, ns_path
from .emitters import Emitter

__all__ = ["standup"]

def standup(domains_list=None, dry_config=False, verbose=True):
    ini_fn = "emitters.ini"
    ini_dir = Path(__file__).parent
    c = ConfigParser()
    with open(ini_dir / ini_fn, "r") as f:
        c.read_file(f, ini_fn)
    emitters = {}
    if domains_list is None:
        domains_list = [*ns]
    for domain in c.sections():
        if domain not in domains_list:
            continue # skip 'DEFAULT' section
        sect = c[domain]
        ns_p = (ns_path / domain)
        assert ns_p.exists() and ns_p.is_dir(), f"{ns_p} not found"
        for name, emit_type in sect.items():
            if verbose:
                print(f"{name}-{emit_type}")
            directory = ns_p / name
            e = getattr(Emitter, emit_type).value
            if dry_config:
                emitter = {"emitter": e, "directory": directory, "name": name, "verbose": verbose}
            else:
                emitter = e(directory=directory, name=name, verbose=verbose)
            #emitters.setdefault(domain, [])
            #emitters[domain].append(emitter)
            emitters.update({domain: emitter})
    return emitters
