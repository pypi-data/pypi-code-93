import click
import hashlib
import json
import os
import sys
from click import echo
from tabulate import tabulate

from nextcodecli.utils import get_logger

log = get_logger('query')

PAGE_SIZE = 100000
MAX_ROWS_TO_DISPLAY = 100


def progress_callback(received, total):
    sys.stdout.write("  {:,} / {:,}    \r".format(received, total))


def get_results(qry, limit, filt, sort, output_file, is_json=False):
    row_count = qry.line_count or 0
    row_count_to_fetch = row_count
    if not output_file and not limit:
        limit = MAX_ROWS_TO_DISPLAY
        echo("No output file. Only fetching {} rows".format(limit))

    if limit:
        row_count_to_fetch = min(limit, row_count)

    if row_count != row_count_to_fetch:
        sys.stderr.write(
            "Retrieving top %s from %s rows of query results." % (row_count_to_fetch, row_count)
        )
    else:
        sys.stderr.write("Retrieving up to %s rows of query results." % (row_count_to_fetch))
    sys.stderr.flush()
    echo("")

    results = qry.get_results(
        row_count_to_fetch, 0, sort, filt, is_json=is_json, callback=progress_callback
    )

    if is_json:
        if output_file:
            with open(os.path.expanduser(output_file), 'w') as f:
                json.dump(results, f, indent=4)
            echo("Results have been written to '%s'" % output_file)
        else:
            echo(json.dumps(results, indent=4))
        return

    echo("")
    if output_file:
        with open(os.path.expanduser(output_file), 'w') as f:
            f.write(results)
        echo("Results have been written to '%s'" % output_file)

    else:
        rows = results.split("\n")
        rows = [r.split('\t') for r in rows]
        if len(rows) > MAX_ROWS_TO_DISPLAY:
            click.echo("Only showing top %s" % MAX_ROWS_TO_DISPLAY)
        tbl = tabulate(rows[1:MAX_ROWS_TO_DISPLAY], headers=rows[0])
        echo(tbl)
