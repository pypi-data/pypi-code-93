from argparse import ArgumentParser
from pathlib import Path
from sys import argv
from typing import NamedTuple, Optional, Sequence


class Arguments(NamedTuple):
    playlistPath: Path
    extraArgs: Sequence[str]


def parse_args(argv: Sequence[str] = argv[1:]) -> Optional[Arguments]:
    parser = ArgumentParser()
    parser.add_argument("scenes", type=Path, help="Scene to present")

    try:
        args, extraArgs = parser.parse_known_args(argv)
    except SystemExit:
        return None

    return Arguments(args.scenes, extraArgs)
