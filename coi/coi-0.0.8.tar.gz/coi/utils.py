import os
import sys
import tty
import termios
import subprocess
from pathlib import Path
from string import Template
from argparse import Namespace
from typing import List, Dict, Union
from functools import lru_cache


@lru_cache()
def get_context() -> Union[Path, None]:
    """
    Return the default template: either a group name or 'none'
    """
    config_dir = get_config_dir()
    matches = list(config_dir.glob('*.default'))
    if len(matches) > 1:
        print("Cannot have multiple .default file")
        sys.exit(1)
    return matches[0] if matches else None


def get_config_dir(root=None) -> Path:
    if root is None:
        root = os.environ.get('XDG_CONFIG_HOME') or os.path.join(
            os.path.expanduser('~'), '.config')
        return Path(os.path.join(root, "coi"))
    else:
        return Path(os.path.join(root, ".coi"))


def get_system_template_path(path=None) -> Path:
    """

    """
    coi_path = Path(__file__).parents[0]
    return coi_path / 'templates'


@lru_cache()
def get_tmpl_paths() -> Dict[str, Path]:
    """
    Return system and user-defined templates' paths
    """
    t_paths = {}
    paths = (get_system_template_path(), get_config_dir(), )
    for p in paths:
        for fname in p.glob('*.tmpl'):
            name = fname.stem
            t_paths[name] = p / fname
    return t_paths


def get_template(fname: Path) -> Template:
    """
    @name: If None, return all templates in the path; otherwise only the chosen
           one
    """
    with open(fname, "r") as f:
        templ = Template(f.read())
    return templ


def get_cmd(args: Namespace) -> str:
    """

    """
    t_name = args.t
    templ = get_template(get_tmpl_paths()[t_name])
    return templ.substitute(vars(args))


def run_cmd(cmd: str):
    """

    """
    subprocess.run(cmd, shell=True,)


def get_char() -> str:
    """
    Get one character from terminal
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
