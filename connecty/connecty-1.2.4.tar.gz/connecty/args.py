
from argparse import ArgumentParser
from pathlib import Path

parser = ArgumentParser()
parser.add_argument("config", type=Path, metavar="CONFIG")
parser.add_argument("-x", default=None, dest="T")
