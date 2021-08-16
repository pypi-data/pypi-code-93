# Copyright 2019 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Automatically generate and overwrite examples of .scl files.

`autoautoscl --help` for more information.
"""

import argparse
import datetime
import logging
import os
import re
import shlex
import subprocess
import sys
import textwrap
import time

logging.basicConfig(level=logging.INFO)

RE_YEARRANGE = re.compile(r"(\d{4})-(\d{4})", re.ASCII)

REPOROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

CURRENTYEAR = int(datetime.date.today().strftime("%Y"))


class Error(Exception):
    """Exceptions to be catched and nicely formatted to the user."""


def auto_fr_educnat(years):
    """Iterate over commands and destination files to run.

    Yields tuples (command, file), where:
    - command is the command to run, as a list to be passed to subprocess.run()
      (working directory being the repository root).
    - file is the name of the destination file
      (absolute, or relative to the repository root):
      standard output of the command is to be written to this file
      (which is overwritten without asking if it already exists).
    """
    for year in years:
        for zone, ville in (("A", "Grenoble"), ("B", "Rennes"), ("C", "Paris")):
            yield (
                ["./bin/autoscl", "fr.educnat", f"{year}-{year+1}", ville],
                f"doc/examples/fr_{year}{year+1}_{zone}.scl",
            )


COUNTRIES = {"fr.educnat": auto_fr_educnat}


def _type_country(text):
    """Check that country is supported."""
    if text in COUNTRIES:
        return text
    raise argparse.ArgumentTypeError(
        "{} is not a valid countries. Choose a string among: {}.".format(
            text, ", ".join(COUNTRIES.keys())
        )
    )


def _type_yearrange(text):
    """Check that year is a range of years (e.g. "2015-2020")."""
    match = RE_YEARRANGE.match(text)
    if not match:
        raise argparse.ArgumentTypeError(
            f"{text} is not a valid year range: it must be of the form YYYY-YYYY (e.g. 2015-2020)."
        )
    start, end = int(match.groups()[0]), int(match.groups()[1])
    return list(range(start, end))


def argumentparser():
    """Return an argument parser."""
    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser(
        description="Generate and overwrite .scl examples.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
                Example: 'autoautoscl fr.educnat 2017-2020' generates the .scl files for French official school years, from 2017 to 2020.

                <french>
                Pour générer les calendriers des trois zones, depuis la racine du projet, utiliser (ajouter éventuellement les années):

                ./bin/autoautoscl
                ./bin/generate_examples.sh

                </french>
                """
        ),
    )
    parser.add_argument(
        "-c",
        "--country",
        help="Country of calendar.",
        default="fr.educnat",
        type=_type_country,
    )
    parser.add_argument(
        "years",
        help="Calendar school years.",
        nargs="?",
        type=_type_yearrange,
        default="{}-{}".format(CURRENTYEAR, CURRENTYEAR + 1),
    )
    return parser


def main():
    """Main function."""
    args = argumentparser().parse_args()
    for command, destfile in COUNTRIES[args.country](args.years):
        time.sleep(2)  # Be kind to the opendata servers.
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            cwd=REPOROOT,
            text=True,
        )
        if completed.returncode == 0:
            with open(os.path.join(REPOROOT, destfile), "w") as stdout:
                stdout.write(completed.stdout)
            logging.info(
                """Command "%s" completed successfully.""", shlex.join(command)
            )
        else:
            logging.error(
                """Command "%s" exited with errors:\n%s""",
                shlex.join(command),
                completed.stderr,
            )


if __name__ == "__main__":
    try:
        if sys.version_info < (3, 8):
            raise Error("This program requires python version 3.8 or above.")
        main()
    except Error as error:
        logging.error(str(error))
        sys.exit(1)
