###########################################################################
#
#  Copyright 2020 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################

import json
import textwrap
import argparse

from starthinker.util.bigquery import get_schema
from starthinker.util.configuration import Configuration
from starthinker.util.configuration import commandline_parser


def main():
  # get parameters
  parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent("""\
    Command line to package a BQ dataset into a workflow.

    Helps developers turn BigQuery datasets into workflows.
    Loads views, reports, and data sources where defined from BQ.
    Constructs a workflow.

    Example:
      `python espresso.py --project [id] --dataset [name] -[u|s] [credentials]`

    Syntax:
      SELECT *
      FROM `dataset.table` /* ESPRESSO: {"dcm":{"report":{"account":"2789", "name":"Campaign Comparison: Jack In The Box"}}} */
      LEFT JOIN 'datset.table` /* ESPRESSO: {"google_api":{"api":"dfareporting", "version":"v3.4", "function":"advertisers.list", "iterate":true, "kwargs":{"accountId":2789}}} */

  """))

  parser.add_argument(
    '--dataset',
    help='name of BigQuery dataset',
    default=None
  )

  # initialize project
  parser = commandline_parser(parser, arguments=('-u', '-c', '-s', '-v', '-p'))
  args = parser.parse_args()
  config = Configuration(
    user=args.user,
    client=args.client,
    service=args.service,
    verbose=args.verbose,
    project=args.project
  )

  auth = 'service' if args.service else 'user'

  # See Anonymize.
  # Loop views.
  # Check for ESPRESSO regexp.
  # Create a prerequisite list.
  # Function per connector?
  # Credentials determined at load.
  # Mimic JSON format of recipe to keep things simple / cohesive.

  if args.csv:

    with open(args.csv, 'r') as csv_file:
      rows = csv_to_rows(csv_file.read())

      if not schema:
        rows, schema = get_schema(rows)
        print('DETECETED SCHEMA', json.dumps(schema))
        print('Please run again with the above schema provided.')
        exit()

      rows_to_table(
        config,
        auth,
        config.project,
        args.dataset,
        args.table,
        rows,
        schema
      )

  elif args.excel_workbook and args.excel_sheet:
    with open(args.excel_workbook, 'r') as excel_file:
      rows = excel_to_rows(excel_file, args.excel_sheet)

      if not schema:
        rows, schema = get_schema(rows)
        print('DETECETED SCHEMA', json.dumps(schema))
        print('Please run again with the above schema provided.')
        exit()

      rows_to_table(
        config,
        auth,
        config.project,
        args.dataset,
        args.table,
        rows,
        schema
      )

  else:
    # print schema
    print(json.dumps(
      table_to_schema(
        config,
        auth,
        config.project,
        args.dataset,
        args.table
      ),
      indent=2
    ))

if __name__ == '__main__':
  main()
