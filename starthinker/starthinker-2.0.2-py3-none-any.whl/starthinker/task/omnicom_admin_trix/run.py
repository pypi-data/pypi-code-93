import json
import os
import csv
import uuid

from starthinker.util.sheets import sheets_read, sheets_id
from starthinker.util.project import project
from starthinker.util.bigquery import io_to_table, get_schema, query_to_rows

output_file_name = '/tmp/%s' % str(uuid.uuid1())


def _load_admin_table():
  if project.verbose:
    print('Omnicom Admin Trix')

  # Read Admin Sheet (format: Name, Sheet URL, Partner ID, Advertiser IDs)
  client_sheet_ids = []
  split = project.task['range'].split('!')
  sheet_name = split[0]
  sheet_range = split[1]

  admin_sheet = sheets_read(project.task['auth'], project.task['sheet_id'],
                            sheet_name, sheet_range)

  output_file = open(output_file_name, 'wb')
  output = csv.writer(output_file)

  # Admin table header
  output.writerow(['Name', 'Sheet_ID', 'Partner_ID', 'Advertiser_ID'])

  # For each row
  for admin_row in admin_sheet[1:]:
    # Parse Sheet ID
    client_sheet_id = sheets_id(project.task['auth'], admin_row[1])
    client_sheet_ids.append(client_sheet_id)

    base_row = [admin_row[0], client_sheet_id, admin_row[2]]

    # If advertiser ids are not present, it means all advertisers under the
    # partner, so pull advertisers from BQ
    if len(admin_row) >= 4 and admin_row[3]:
      advertisers = [
          int(advertiser.strip()) for advertiser in admin_row[3].split(',')
      ]
    else:
      advertisers = [
          advertiser[0] for advertiser in query_to_rows(
              project.task['auth'],
              project.id,
              project.task['dataset'],
              'select advertiser_id from starthinker_v2.Advertiser where partner_id = %d'
              % int(admin_row[2]),
              row_max=None,
              legacy=True)
      ]

    for advertiser_id in advertisers:
      # For each advertiser, add row to output (format: Name, Sheet ID, Partner ID, Advertiser ID)
      output.writerow(base_row + [advertiser_id])

  output_file.close()

  # Load Admin table, overwriting existing content
  rows, schema = get_schema(
      [['Name', 'Sheet_ID', 'Partner_ID', 'Advertiser_ID']], True, True)
  io_to_table(
      project.task['auth'],
      project.id,
      project.task['dataset'],
      project.task['table'],
      open(output_file_name, 'rb'),
      'CSV',
      schema=schema,
      skip_rows=1)

  os.remove(output_file_name)

  return client_sheet_ids


def _load_client_sheet(client_sheet_ids, sheet_name, sheet_range, table_name):
  output_file = open(output_file_name, 'wb')
  output = csv.writer(output_file)

  # For each input sheet
  for client_sheet_id in client_sheet_ids:

    # Reed the input sheet
    client_sheet = sheets_read(project.task['auth'], client_sheet_id,
                               sheet_name, sheet_range)

    # Add header with additional Sheet ID column
    output.writerow(client_sheet[0] + ['Sheet_ID'])

    # Inject sheet id in each row, and add to output
    for row in client_sheet[1:]:
      output.writerow(row + [client_sheet_id])

  # Upload to Big Query
  output_file.close()

  rows, schema = get_schema([client_sheet[0] + ['Sheet_ID']], True, True)
  io_to_table(
      project.task['auth'],
      project.id,
      project.task['dataset'],
      table_name,
      open(output_file_name, 'rb'),
      'CSV',
      schema=schema,
      skip_rows=1)

  #os.remove(output_file_name)


@project.from_parameters
def omnicom_admin_trix():
  # Step1: Load admin trix replacing the sheet URL with just the sheet ID, and
  # splitting the advertisers
  client_sheet_ids = _load_admin_table()

  # Step 2: Load each client specific sheet injecting the sheet ID in each row
  _load_client_sheet(client_sheet_ids, 'Traders', 'A1:C', 'traders')
  _load_client_sheet(client_sheet_ids, 'Impression_Goals', 'A1:C',
                     'impression_goals')
  _load_client_sheet(client_sheet_ids, 'Advertisers', 'A1:E',
                     'advertiser_budget')


if __name__ == '__main__':
  omnicom_admin_trix()
