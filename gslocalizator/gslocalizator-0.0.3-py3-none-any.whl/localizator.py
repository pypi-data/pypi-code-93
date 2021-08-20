from __future__ import print_function
from gslocalizator.parser import WordsParser
from typing import Dict, List, Optional, Callable
from gslocalizator.sheet_tran_task import _SheetTranTask
from pprint import pprint
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os.path
from googleapiclient import discovery
from googleapiclient.discovery import build
# from googleapiclient import *

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


class GoogleSheetLocalizator:

    @staticmethod
    def open(credsFile, sheetId):
        gsl = GoogleSheetLocalizator(credsFile, sheetId)
        gsl.__enter__()
        return gsl

    tran_tasks: List[_SheetTranTask]

    def reset(self):
        self.tran_tasks.clear()

    def close(self):
        self.__exit__(None, None, None)

    def tran(self,
             from_sheet_range: str,
             from_value_column_to_file: Dict[str, str],
             with_key_column: Optional[str] = '',
             exclude_headers: Optional[List[str]] = ['//'],
             cell_formater: Optional[Callable[[str], str]] = (lambda s: s),
             key_formater: Optional[Callable[[str], str]] = (lambda s: s),
             ) -> "GoogleSheetLocalizator":
        '''
        Setting localizator info.

        Parameters
        ----------
        - from_sheet_range: str From witch sheet and range. Format 'sheet_name!from:to' from/to can be cell or column.
        - from_value_column_to_file: Dict[str, str]  If withKeyColumn == none 1st column will be key.
        - with_key_column: Optional[str] withKeyColumn: If withKeyColumn == none 1st column will be key.
        - exclude_headers: Optional[List[str]]  If there is an excludeHeader in your keyColumn then ignore this Row

        Returns
        -------
        self

        '''
        self.tran_tasks.append(_SheetTranTask(
            from_sheet_range=from_sheet_range,
            from_value_column_to_file=from_value_column_to_file,
            with_key_column=with_key_column,
            exclude_headers=exclude_headers,
            cell_formater=cell_formater,
            key_formater=key_formater
        ))
        return self

    def _get_ranges_from_tran_tasks(self) -> List[str]:
        ranges = []
        for task in self.tran_tasks:
            ranges.append(task.get_sheetname_from_range())
        return ranges

    def request(self) -> WordsParser:
        '''
        Set save result format as iOS and execute tran tasks
        '''
        ranges = self._get_ranges_from_tran_tasks()
        return self._request_multiple_range(ranges)

    def __init__(self, credsFile, sheetId):
        self.creds = self._init_creds(credsFile)
        self.sheetId = sheetId
        self.tran_tasks = []

    def __enter__(self):
        self.service = build('sheets', 'v4', credentials=self.creds)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.service.close()

    def _init_creds(self, credsFile):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credsFile, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def _request_multiple_range(self, ranges: List[str]) -> WordsParser:
        request = self.service.spreadsheets().values().batchGet(
            spreadsheetId=self.sheetId,
            ranges=ranges,
            valueRenderOption='UNFORMATTED_VALUE',
            dateTimeRenderOption='SERIAL_NUMBER')
        try:
            print(f'requesting:{ranges}')
            response = request.execute()
            wp = WordsParser(response, self.tran_tasks)
            return wp
        except Exception as e:
            print('Error response : ')
            pprint(e)
