
import sys
import os.path
from typing import List, Union
from superprocessor import cmd

from pips.crawl import show_stats
from pips.cli import parse_cmd_result
from pips.verifier import init_pips, verify_action


class PIP:

    default_path = [
        sys.executable,
        '-m',
        'pip',
    ]

    def __init__(self):
        init_pips()

    def do(self,
           op:              str,
           packages:        List[str],
           executable_path: Union[List[str], None] = None,
           verbose:         bool = True):
        executable_path = (
                executable_path or self.default_path
        )

        show_stats(packages)

        stmt = [
            * self.default_path,
            op,
            * packages,
        ]

        if op in [
            'uninstall'
        ]:
            stmt.append('--yes')

        if verify_action():
            out, err, status = cmd(*stmt, log=False)
            parse_cmd_result(out, err, status, op, verbose=True)
