import time
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from starthinker.util.data import get_rows
from starthinker.util.auth import get_credentials
from starthinker.util.storage import media_download
from starthinker.util.csv import column_header_sanitize

from googleapiclient import discovery

from starthinker.util.storage import object_put

from starthinker.util.bigquery import io_to_table, table_create

from starthinker.task.sdf.schema.Lookup import SDF_Field_Lookup

from starthinker.util.google_api import API_DV360

import io
import zipfile
from io import BytesIO

import apitools.base.py as apitools_base

LINE_ITEM_SCHEMA = [{
    'name': 'Line_Item_Id',
    'type': 'INTEGER',
    'mode': 'NULLABLE'
}, {
    'name': 'Io_Id',
    'type': 'INTEGER',
    'mode': 'NULLABLE'
}, {
    'name': 'Type',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Subtype',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Name',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Timestamp',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Status',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Start_Date',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'End_Date',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Budget_Type',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Budget_Amount',
    'type': 'FLOAT',
    'mode': 'NULLABLE'
}, {
    'name': 'Pacing',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Pacing_Rate',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Pacing_Amount',
    'type': 'FLOAT',
    'mode': 'NULLABLE'
}, {
    'name': 'Frequency_Enabled',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Frequency_Exposures',
    'type': 'INTEGER',
    'mode': 'NULLABLE'
}, {
    'name': 'Frequency_Period',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Frequency_Amount',
    'type': 'INTEGER',
    'mode': 'NULLABLE'
}, {
    'name': 'Trueview_View_Frequency_Enabled',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Trueview_View_Frequency_Exposures',
    'type': 'INTEGER',
    'mode': 'NULLABLE'
}, {
    'name': 'Trueview_View_Frequency_Period',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Partner_Revenue_Model',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Partner_Revenue_Amount',
    'type': 'FLOAT',
    'mode': 'NULLABLE'
}, {
    'name': 'Conversion_Counting_Type',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Conversion_Counting_Pct',
    'type': 'FLOAT',
    'mode': 'NULLABLE'
}, {
    'name': 'Conversion_Floodlight_Activity_Ids',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Fees',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Integration_Code',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Details',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Bid_Strategy_Type',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Bid_Strategy_Value',
    'type': 'FLOAT',
    'mode': 'NULLABLE'
}, {
    'name': 'Bid_Strategy_Unit',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Bid_Strategy_Do_Not_Exceed',
    'type': 'FLOAT',
    'mode': 'NULLABLE'
}, {
    'name': 'Apply_Floor_Price_For_Deals',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Creative_Assignments',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Geography_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Geography_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Geography_Regional_Location_List_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Geography_Regional_Location_List_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Language_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Language_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Device_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Device_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Browser_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Browser_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Digital_Content_Labels_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Brand_Safety_Sensitivity_Setting',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Brand_Safety_Custom_Settings',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Third_Party_Verification_Services',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Third_Party_Verification_Labels',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Channel_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Channel_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Site_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Site_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'App_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'App_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'App_Collection_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'App_Collection_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Category_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Category_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Keyword_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Keyword_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Keyword_List_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Audience_Targeting_Similar_Audiences',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Audience_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Audience_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Affinity_and_In_Market_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Affinity_and_In_Market_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Custom_List_Targeting',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Inventory_Source_Targeting_Authorized_Seller_Options',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Inventory_Source_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Inventory_Source_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Inventory_Source_Targeting_Target_New_Exchanges',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Daypart_Targeting',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Daypart_Targeting_Time_Zone',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Environment_Targeting',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Viewability_Targeting_Active_View',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Position_Targeting_On_Screen',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Position_Targeting_Display_Position_In_Content',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Position_Targeting_Video_Position_In_Content',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Position_Targeting_Audio_Position_In_Content',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Video_Player_Size_Targeting',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Demographic_Targeting_Gender',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Demographic_Targeting_Age',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Demographic_Targeting_Household_Income',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Demographic_Targeting_Parental_Status',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Connection_Speed_Targeting',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Carrier_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Carrier_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Bid_Multipliers',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Video_Ad_Formats',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Bid_Strategy_Type',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Bid_Strategy_Value',
    'type': 'FLOAT',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Mobile_Bid_Adjustment_Option',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Mobile_Bid_Adjustment_Percentage',
    'type': 'INTEGER',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Desktop_Bid_Adjustment_Option',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Desktop_Bid_Adjustment_Percentage',
    'type': 'INTEGER',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Tablet_Bid_Adjustment_Option',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Tablet_Bid_Adjustment_Percentage',
    'type': 'INTEGER',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Connected_TV_Bid_Adjustment_Option',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Connected_TV_Bid_Adjustment_Percentage',
    'type': 'INTEGER',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Category_Exclusions_Targeting',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Content_Filter',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Inventory_Source_Targeting',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Third_Party_Viewability_Vendor',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'TrueView_Third_Party_Brand_Safety_Vendor',
    'type': 'STRING',
    'mode': 'NULLABLE'
}]

AD_GROUP_SCHEMA = [{
    'name': 'Ad_Group_Id',
    'type': 'INTEGER',
    'mode': 'NULLABLE'
}, {
    'name': 'Line_Item_Id',
    'type': 'INTEGER',
    'mode': 'NULLABLE'
}, {
    'name': 'Name',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Status',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Video_Ad_Format',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Bid_Cost',
    'type': 'FLOAT',
    'mode': 'NULLABLE'
}, {
    'name': 'Popular_Videos_Bid_Adjustment',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Keyword_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Keyword_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Category_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Category_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Placement_Targeting_YouTube_Channels_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Placement_Targeting_YouTube_Channels_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Placement_Targeting_YouTube_Videos_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Placement_Targeting_YouTube_Videos_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Placement_Targeting_YouTube_URLs_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Placement_Targeting_YouTube_URLs_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Placement_Targeting_Apps_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Placement_Targeting_Apps_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Placement_Targeting_App_Collections_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Placement_Targeting_App_Collections_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Demographic_Targeting_Gender',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Demographic_Targeting_Age',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Demographic_Targeting_Household_Income',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Demographic_Targeting_Parental_Status',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Audience_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Audience_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Affinity_and_In_Market_Targeting_Include',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Affinity_and_In_Market_Targeting_Exclude',
    'type': 'STRING',
    'mode': 'NULLABLE'
}, {
    'name': 'Custom_List_Targeting',
    'type': 'STRING',
    'mode': 'NULLABLE'
}]


def sdf_read(project):
  # Read Filter Ids
  filter_ids = list(
      get_rows(project.task['auth'], project.task['sdf']['read']['filter_ids']))

  # todo handle inventory sources
  body = {
      'version': project.task['sdf']['version'],
      'partnerId': project.task['sdf']['partner_id'],
      'parentEntityFilter': {
          'fileType': project.task['sdf']['file_types'],
          'filterType': project.task['sdf']['filter_type'],
          'filterIds': filter_ids
      },
      'idFilter': None
  }

  operation = API_DV360('user').sdfdownloadtasks().create(body=body).execute()

  print('operation====================')
  print(operation)

  if operation or 'name' not in operation:
    request = API_DV360('user').sdfdownloadtasks().operations().get(
        name=operation['name'])
    # This is the eng recommended way of getting the operation
    while True:
      response = request.execute()
      if 'done' in response and response['done']:
        break
      time.sleep(30)
  else:
    print('error')
    #todo error checking if operation is non null

  print('response====================')
  print(response)

  request = API_DV360('user').media().download_media(resourceName=resource_name)

  data = media_download(request, CHUNK_SIZE, encoding=None)


def dt_move_large(data, table_name, jobs):
  if project.verbose:
    print('DT TO TABLE LARGE', dt_partition)

  delimiter = '\n'
  disposition = 'WRITE_TRUNCATE'

  # decompression handler for gzip ( must be outside of chunks as it keeps track of stream across multiple calls )
  gz_handler = zlib.decompressobj(32 + zlib.MAX_WBITS)

  # sliding view of data flowing out of decompression, used to buffer and delimit rows
  first_row = True
  view = ''

  # loop all chunks of file, decompress, and find row delimiter
  for data_gz in data:

    view += gz_handler.decompress(data_gz.read()).decode()

    if first_row:
      end = view.find(delimiter)
      schema = dt_schema(view[:end].split(','))
      view = view[(end + 1):]
      first_row = False

    end = view.rfind(delimiter)

    jobs.append(
        io_to_table(project.task['auth'], project.id,
                    project.task['to']['dataset'], table_name,
                    StringIO(view[:end]), 'CSV', schema, 0, disposition, False))
    disposition = 'WRITE_APPEND'
    view = view[min(end + 1, len(view)):]


def sdf_schema(header):
  schema = []
  for h in header:
    h = column_header_sanitize(h)
    schema.append({
        'name': h,
        'type': DT_Field_Lookup.get(h, 'STRING'),
        'mode': 'NULLABLE'
    })
  return schema

  # with zipfile.ZipFile(data) as d:
  #   print(d)
  #   print(d.infolist())
  #   print(d.namelist())
  #   file_names = d.namelist()
  #   for file_name  in file_names:
  #     print('file name======================================')
  #     print(file_name)
  #     if 'Skipped' in file_name:
  #       continue
  #     with d.open(file_name) as file:

  #       wrapper = io.TextIOWrapper(file, encoding='utf-8')
  #       schema = None

  #       #todo terwilleger figure out the schema piece of this
  #       # remember that the header was actually in the document so could try that

  #       if file_name == 'SDF-AdGroups.csv':
  #         schema = AD_GROUP_SCHEMA
  #       elif file_name == 'SDF-LineItems.csv':
  #         schema = LINE_ITEM_SCHEMA

  #       table_name = 'SDF_' + file_name.split('.')[0].split('-')[1]
  #       disposition = 'WRITE_TRUNCATE'
  #       if project.task['sdf']['daily']:
  #         disposition = 'WRITE_APPEND'
  #         table_create('service', project.id, project.task['sdf']['out']['bigquery']['dataset'], table_name, is_time_partition=True)
  #         #todo terwilleger add something here that creates the time partitioned table if it doesn't exist

  #       io_to_table('service', project.id, project.task['sdf']['out']['bigquery']['dataset'], table_name, wrapper, schema=schema, skip_rows=1, disposition=disposition)


#todo flag for if delete temp tables


def sdf_schema(header):
  schema = []

  for h in header:
    schema.append({
        'name': column_header_sanitize(h),
        'type': SDF_Field_Lookup.get(h, 'STRING'),
        'mode': 'NULLABLE'
    })

  return schema


def download_media(auth, resource_name):
  data = BytesIO()

  request = API_DV360('user').media().download_media(resourceName=resource_name)

  downloader = MediaIoBaseDownload(data, request)

  download_finished = False
  while download_finished is False:
    _, download_finished = downloader.next_chunk()

  return data
