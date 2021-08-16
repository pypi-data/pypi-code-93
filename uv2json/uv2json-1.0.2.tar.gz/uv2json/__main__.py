"""Convert a UV File to JSON.

Takes a CSV file output by Gilson GX machines and converts it into a JSON file containing sample information alongwith intensities and time for three different UV wavelengths.
"""

from argparse import ArgumentParser
from uv2json import uv2json


def main():
    parser = ArgumentParser(description="Convert Gilson CSV to JSON file")
    parser.add_argument(
        "filenames",
        help="convert given filename(s) to json",
        nargs="+",
    )

    args = parser.parse_args()
    uv2json.convert(args.filenames)


if __name__ == "__main__":
    main()
