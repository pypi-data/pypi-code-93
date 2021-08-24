"""
badgey
Generate badges for your projects

Usage:
    badgey [options] <badge> [<badge_args>...]
    badgey -l

-l, --list              List the available badges
-h, --help              Show current help message
-v, --version           Print version
"""
from .__version__ import __version__

from collections import namedtuple
from inspect import cleandoc
from typing import Dict

from docopt import docopt
from jinja2 import Template

from .badges import CoverageBadge, LOCBadge
from ._base import badges

__all__ = [CoverageBadge, LOCBadge]


def print_badges(badges: Dict[str, namedtuple]):
    PRINT_TEMPLATE = r"""
    Available Badges:

    {%- for name, entry in badges.items() %}
    - {{ name }}
        {{ entry.doc | indent(4) }}

        Args:
        {%- for arg in entry.args %}
        - {{ arg }}
        {% endfor %}
    {% endfor %}
    """
    template = Template(cleandoc(PRINT_TEMPLATE))

    print(template.render(badges=badges))


def main():
    args = docopt(__doc__, version=f"badgey {__version__}")

    if args["--list"]:
        print_badges(badges)
        return

    badge_name = args["<badge>"]
    badge_args = args["<badge_args>"]

    Badge = badges[badge_name].cls
    badge = Badge(*badge_args)
    badge.write()
