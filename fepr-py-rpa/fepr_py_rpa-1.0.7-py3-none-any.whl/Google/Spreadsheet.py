from googleapiclient.discovery import build
import pickle
import os
import pandas as pd
from pandas.core.frame import DataFrame
from ..logger import logger


class SpreadsheetMetadata(object):
    def __init__(self, sheet_title: list, sheet_id: list):
        self.sheet_titles = sheet_title
        self.sheet_ids = sheet_id

    @property
    def sheet_meta_dict(self) -> list:
        meta_dict: dict = {}
        meta_list: list = []
        for i in range(len(self.sheet_titles)):
            meta_dict['title'] = self.sheet_titles[i]
            meta_dict['id'] = self.sheet_ids[i]
            meta_list.append(meta_dict.copy())

        return meta_list


class Spreadsheet(object):
    def __init__(self, spreadsheet_id: str):

        self.spreadsheet_id = spreadsheet_id

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                cred = pickle.load(token)
        self.spreadsheet = build(
            'sheets', 'v4', cache_discovery=False, credentials=cred).spreadsheets()

    def load_table(self, range_: str) -> DataFrame:
        result = self.spreadsheet.values().get(
            spreadsheetId=self.spreadsheet_id, range=range_).execute()

        logger.info({
            'action': 'get_table',
            'status': 'running',
            'message': {
                'range': range_
            }
        })
        values = result.get('values', [])
        sheet = pd.DataFrame(values, columns=values[0])
        sheet = sheet.drop(0)
        sheet = sheet.reset_index(drop=True)

        logger.info({
            'action': 'get_table',
            'status': 'Success!',
        })
        return sheet

    def load_values(self, range_: str) -> list:
        result = self.spreadsheet.values().get(
            spreadsheetId=self.spreadsheet_id, range=range_).execute()
        values = result.get('values', [])
        logger.info({
            'action': 'get_values',
            'status': 'Success!',
        })
        return values

    def append_dataframe(self, range_: str, dataframe: DataFrame):
        logger.info({
            'action': 'set_dataframe',
            'status': 'running',
            'message': {
                'value': range_
            }
        })
        self.spreadsheet.values().append(spreadsheetId=self.spreadsheet_id,
                                         valueInputOption="USER_ENTERED",
                                         insertDataOption='OVERWRITE',
                                         range=range_,
                                         body={"values": dataframe.values.tolist()}).execute()

        logger.info({
            'action': 'set_dataframe',
            'status': 'Success!',
        })

    def set_values(self, range_: str, values: list):
        self.spreadsheet.values().update(spreadsheetId=self.spreadsheet_id,
                                         valueInputOption="USER_ENTERED",
                                         range=range_,
                                         body={"values": values}).execute()
        logger.info({
            'action': 'set_values',
            'status': 'Success!',
        })

    def load_metadata(self) -> list:
        sheet_metadata = self.spreadsheet.get(
            spreadsheetId=self.spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')

        sheet_title_list = [Sheet_Name["properties"]["title"]
                            for Sheet_Name in sheets]

        sheet_id_list = [Sheet_id["properties"]["sheetId"]
                         for Sheet_id in sheets]

        metadata = SpreadsheetMetadata(sheet_title_list, sheet_id_list)
        return metadata.sheet_meta_dict

    def create_sheet(self, sheet_name: str):
        requests = [{
            'addSheet': {
                "properties": {
                    "title": sheet_name
                }
            }
        }]

        logger.info({
            'action': 'create_sheet',
            'status': 'running',
            'message': {
                'sheet_name': sheet_name
            }
        })

        body = {'requests': requests}
        response = self.spreadsheet.batchUpdate(
            spreadsheetId=self.spreadsheet_id, body=body).execute()
        sheetid = response['replies'][0]['addSheet']['properties']['sheetId']
        return {'sheet_id': sheetid}

    def delete_sheet(self, sheet_id: str):
        requests = [{
            'deleteSheet': {
                "sheetId": sheet_id
            }
        }]

        logger.info({
            'action': 'delete_sheet',
            'status': 'running',
            'message': {
                'sheet_id': sheet_id
            }
        })

        body = {'requests': requests}
        self.spreadsheet.batchUpdate(
            spreadsheetId=self.spreadsheet_id, body=body).execute()

        logger.info({
            'action': 'delete_sheet',
            'status': 'Success!'
        })

    def clear_range(self, range_: str):
        self.spreadsheet.values().clear(spreadsheetId=self.spreadsheet_id,
                                        range=range_, body={}).execute()
        
        logger.info({'action': 'clear_range', 'status': 'Success!'})
