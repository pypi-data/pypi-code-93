from string import Template
from pathlib import Path
from argparse import Namespace


def get_template_path(path=None) -> Path:
    """

    """
    coi_path = Path(__file__).parents[0]
    return coi_path / 'templates'


# val = subprocess.check_call("./script.sh '%s'" % arg, shell=True)
# subprocess.run()

def get_cmd(args: Namespace) -> str:
    """

    """
    # load template string
    fname = get_template_path() / 'c-on-i'
    with open(fname, "r") as f:
        templ = Template(f.read())
    return templ.substitute(vars(args))
