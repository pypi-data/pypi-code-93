# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""Interface for searching for packages"""

from portmod.query import display_search_results, query
from portmodlib.l10n import l10n


def search_main(args):
    if args.description:
        pkgs = query(
            ["NAME", "ATOM", "DESC"],
            " ".join(args.query),
            strip=True,
            squelch_sep=True,
            insensitive=True,
        )
    else:
        pkgs = query(
            ["NAME", "ATOM"],
            " ".join(args.query),
            strip=True,
            squelch_sep=True,
            insensitive=True,
        )

    display_search_results(pkgs)


def add_search_parser(subparsers, parents):
    parser = subparsers.add_parser("search", help=l10n("search-help"), parents=parents)
    parser.add_argument(
        "query",
        metavar=l10n("query-placeholder"),
        help=l10n("search-query-help"),
        nargs="+",
    )
    parser.add_argument(
        "-d", "--description", help=l10n("searchdesc-help"), action="store_true"
    )
    parser.set_defaults(func=search_main)
