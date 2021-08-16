from typing import Optional
import os

def sh(
    cmd: str,
    debug: bool = False
) -> str:
    import subprocess

    if debug:
        print(cmd)

    return subprocess.getoutput(cmd)

def path(path: str) -> str:
    return path.replace(' ', '\\ ').replace('\\\\ ', '\\ ')

def pwd(debug: bool = False) -> str:
    return sh('pwd', debug=debug)

def ls(
    p: Optional[str] = None,
    debug: bool = False
) -> str:
    return sh('ls{}'.format(' {}'.format(path(p)) if p else ''), debug=debug)

def touch(
    p: str,
    debug: bool = False
) -> str:
    return sh('touch {}'.format(path(p)), debug=debug)

def mkdir(
    p: str,
    debug: bool = False
) -> str:
    return sh('mkdir {}'.format(path(p)), debug=debug)

def rmdir(
    p: str,
    debug: bool = False
) -> str:
    return sh('rmdir {}'.format(path(p)), debug=debug)

def uname(debug: bool = False) -> str:
    return sh('uname', debug=debug)

def rm(
    p: str,
    rf: bool = False,
    debug: bool = False
) -> str:
    return sh('rm{} {}'.format(' -rf' if rf else '', path(p)), debug=debug)

def rmrf(
    p: str,
    debug: bool = False
) -> str:
    return rm(p, rf=True, debug=debug)

def cp(
    from_path: str,
    to_path: str,
    debug: bool = False
) -> str:
    return sh('cp {} {}'.format(path(from_path), path(to_path)), debug=debug)

def mv(
    from_path: str,
    to_path: str,
    debug: bool = False
) -> str:
    return sh('mv {} {}'.format(path(from_path), path(to_path)), debug=debug)