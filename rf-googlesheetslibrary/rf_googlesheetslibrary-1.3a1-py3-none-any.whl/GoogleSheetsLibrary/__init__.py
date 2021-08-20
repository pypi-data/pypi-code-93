# Copyright (C) 2019 Spiralworks Technologies Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from robotlibcore import HybridCore, keyword
from robot.api import logger


__version__ = '1.3a1'


class GoogleSheetsLibrary(HybridCore):
    """``GoogleSheetsLibrary`` is a Robot Framework Library for interfacing tests with Google Sheets using the             \
        ``Google Sheets API v4``.

        This document will try to explain how to use this library and how to integrate it to your robot test suites.


        = OAuth 2.0 Scope Information for the Google Sheets API =
         Refer to the table for the available scopes.
        | =Scope=                                                | =Meaning=                                                    |
        | https://www.googleapis.com/auth/spreadsheets.readonly  | Allows read-only access to the user's sheets and their   \
                                                                   properties.                                                  |
        | https://www.googleapis.com/auth/spreadsheets           | Allows read/write access to the user's sheets and their  \
                                                                   properties.                                                  |
        | https://www.googleapis.com/auth/drive.readonly         | Allows read-only access to the user's file metadata and  \
                                                                   file content.                                                |
        | https://www.googleapis.com/auth/drive.file             | Per-file access to files created or opened by the app.       |
        | https://www.googleapis.com/auth/drive                  | Full, permissive scope to access all of a user's files.  \
                                                                   Request this scope only when it is strictly necessary.       |

        = Generating a Pickle token file =
        The library is set to only accept already generated token stored in a .pickle file.

        You can read more about pickle file here -> https://docs.python.org/3/library/pickle.html.

        Generating a pickle token can easily be done by using the code snippet below. Just replace the variables to        \
            generate your token.

        Before running the code below, first enable Google Sheets API on your account. Place the credentials.json file in  \
            the same directory as the snippet will be.

        Simply follow this quickstart guide from Google Sheets API v4                                                      \
            https://developers.google.com/sheets/api/quickstart/python.

        | from __future__ import print_function
        | import pickle
        | import os.path
        | from googleapiclient.discovery import build
        | from google_auth_oauthlib.flow import InstalledAppFlow
        | from google.auth.transport.requests import Request
        |
        | # This will be the scopes that will be set in your token file.
        | # Modify the scopes you want your token to have, you can use more than one, this needs to be list.
        | SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        | SPREADSHEET_ID = 'your spreadsheet id here.'
        |
        | def main():
        |   creds = None
        | # The file token.pickle stores the user's access and refresh tokens, and is
        | # created automatically when the authorization flow completes for the first
        | # time.
        |   if os.path.exists('token.pickle'):
        |       with open('token.pickle', 'rb') as token:
        |           creds = pickle.load(token)
        | # If there are no (valid) credentials available, let the user log in.
        |   if not creds or not creds.valid:
        |       if creds and creds.expired and creds.refresh_token:
        |           creds.refresh(Request())
        |       else:
        |           flow = InstalledAppFlow.from_client_secrets_file(
        |               'credentials.json', SCOPES)
        |           creds = flow.run_local_server(port=0)
        |   # Save the credentials for the next run
        |   with open('token.pickle', 'wb') as token:
        |       pickle.dump(creds, token)
        |
        | if __name__ == '__main__':
        |   main()
        Run the snippet like any other python code.

        = Reading Google Sheets Ranges =
        The Sheets API allows you to read values from cells, ranges, sets of ranges and entire sheets.
        For these examples, assume the spreadsheet being read has the following data in its first sheet ("Sheet1"):
        |                   | =A=               | =B=           | =C=                   | =D=                                   |
        | =1=               | Item              | Cost          | Stocked               | Ship Date                             |
        | =2=               | Wheel             | $20.50        | 4                     | 3/1/2016                              |
        | =3=               | Door              | $15           | 2                     | 3/15/2016                             |
        | =4=               | Engine            | $100          | 1                     | 3/20/2016                             |
        | =5=               | Totals            | $135.5        | 7                     | 3/20/2016                             |

        == Reading from a Single Range ==

        Reading the value/s of a single range can be done by using `Fetch Single Range` Keyword.

        Example:

         - To be able to read the all the data from ``Item`` column up to the ``Stocked`` column. We can address it by:
        | `Fetch Single Range`          | Sheet1!A1:C           |# fetches all columns starting from A1 up to C5                |

         - To be able to read the all the data from ``Item`` column up to the ``Stocked`` column but, we only want to fetch \
             up to 3 rows, We can do so by:
        | `Fetch Single Range`          | Sheet1!A1:C3          | # fetches all data in A-C columns but only fetches data   \
                                                                    up to the 3rd row.                                          |

        == Reading from Multiple Ranges ==

        Examples:

         - To read multiple ranges from the initialized spreadsheet, It is useful to use `Fetch Multiple Range`
           Keyword.
        | @{ranges}                 | Create List               | Sheet1!A1:E       | Sheet1!A1:E1  |
        | `Fetch Multiple Range`    | ${ranges}                 |                   |               |
        | ${data_from_range}        | `Fetch Multiple Range`    | ${ranges}         |               |

        == valueRenderOption ==

        Data returned could be set using the ``valueRenderOption``. Refer below for the options that could be passed.

        | =Options=                 | =Description=                                                                             |
        | FORMATTED_VALUE           | Values will be calculated & formatted in the reply according to the cell's formatting.\
                                         Formatting is based on the spreadsheet's locale, not the requesting user's locale. \
                                             For example, if A1 is 1.23 and A2 is =A1 and formatted as currency, then A2    \
                                                 would return "$1.23".                                                          |
        | UNFORMATTED_VALUE         | Values will be calculated, but not formatted in the reply. For example, if A1 is 1.23 \
                                        and A2 is =A1 and formatted as currency, then A2 would return the number 1.23.          |
        | FORMULA                   | Values will not be calculated. The reply will include the formulas. For example, if A1\
                                        is 1.23 and A2 is =A1 and formatted as currency, then A2 would return "=A1".            |

        Examples:

        | Fetch Single Range        | Sheet1!A1:C   | valueRenderOption=FORMATTED_VALUE  | # Returns sheet values in the    \
                                                        selected range in a formatted value.                                    |
        | Fetch Single Range        | Sheet1!A1:C   | valueRenderOption=FORMULA          | # Returns the formula applied on \
                                                                                            the selected range.                 |
        | Fetch Multiple Range      | @{ranges}     | valueRenderOption=UNFORMATTED_DATA | # Returns the raw values from the\
                                                                                            selected ranges.                    |

        = Writing to Google Sheet Ranges =

        == BatchUpdateValuesRequest ==

        Sets values in one or more ranges of a spreadsheet. The caller must specify the spreadsheet ID, a `valueInputOption`, \
            and one or more `ValueRange`.

        === Request Body ===
        The request body contains data with the following structure:
        |  {
        |     "valueInputOption": enum (`ValueInputOption`),
        |     "data": [
        |       {
        |         object (`ValueRange`)
        |       }
        |     ],
        |     "includeValuesInResponse": boolean,
        |     "responseValueRenderOption": enum (`ValueRenderOption`),
        |     "responseDateTimeRenderOption": enum (DateTimeRenderOption)
        |  }

        | =Fields=                      | =Input=                       | =Description=                                         |
        | valueInputOption              | enum (ValueInputOption)       | How the input data should be interpreted.             |
        | data[]                        | object (ValueRange)           | The new values to apply to the spreadsheet            |
        | includeValuesInResponse       | boolean                       | Determines if the update response should include  \
                                                                          the values of the cells that were updated. By     \
                                                                          default, responses do not include the updated     \
                                                                          values. The updatedData field within each of the  \
                                                                          BatchUpdateValuesResponse.responses will contain  \
                                                                          the updated values. If the range to write was     \
                                                                          larger than the range actually written, the       \
                                                                          response will include all values in the requested \
                                                                          range (excluding trailing empty rows and columns).    |
        | responseValueRenderOption     | enum (ValueRenderOption)      | Determines how values in the response should be   \
                                                                          rendered. The default render option is            \
                                                                          ValueRenderOption.FORMATTED_VALUE.                    |
        | responseDateTimeRenderOption  | enum (DateTimeRenderOption)   | Determines how dates, times, and durations in the \
                                                                          response should be rendered. This is ignored if   \
                                                                          responseValueRenderOption is FORMATTED_VALUE.     \
                                                                          The default dateTime render option is             \
                                                                          DateTimeRenderOption.SERIAL_NUMBER.                   |
        === Response Body ===
        If successful, the response body contains data with the following structure:
        The response when updating a range of values in a spreadsheet.

        | {
        |   "spreadsheetId": string,
        |   "totalUpdatedRows": number,
        |   "totalUpdatedColumns": number,
        |   "totalUpdatedCells": number,
        |   "totalUpdatedSheets": number,
        |   "responses": [
        |       {
        |           object (UpdateValuesResponse)
        |       }
        |   ]
        | }

        = Types =

        == DateTimeRendedOption ==
        Determines how dates should be rendered in the output

        | = Enums =                 | Description                                                                               |
        | SERIAL_NUMBER             | Instructs date, time, datetime, and duration fields to be output as doubles in        \
                                      "serial number" format, as popularized by Lotus 1-2-3. The whole number portion of the\
                                      value (left of the decimal) counts the days since December 30th 1899. The fractional  \
                                      portion (right of the decimal) counts the time as a fraction of the day. For example, \
                                      January 1st 1900 at noon would be 2.5, 2 because it's 2 days after December 30st 1899,\
                                      and .5 because noon is half a day. February 1st 1900 at 3pm would be 33.625. This     \
                                      correctly treats the year 1900 as not a leap year.                                        |
        | FORMATTED_STRING          | Instructs date, time, datetime, and duration fields to be output as strings in their  \
                                      given number format (which is dependent on the spreadsheet locale).                       |

        == Dimension ==
        Indicates which dimension an operation should apply to.

        | Enums                     |                                                   |
        | DIMENSION_UNSPECIFIED     | The default value, do not use.                    |
        | ROWS                      | Operates on the rows of a sheet                   |
        | COLUMNS                   | Operates on the columns of a sheet                |

        == DimensionRange ==
        A range along a single dimension on a sheet. All indexes are zero-based. Indexes are half open: \
            the start index is inclusive and the end index is exclusive. \
                Missing indexes indicate the range is unbounded on that side.

         - json representation
        | {
        |   "sheetId" : number,
        |   "dimension" : enum (`Dimension`),
        |   "startIndex" : number,
        |   "endIndex" : number
        | }

        | =Fields               | =Type=                    | Description                                                       |
        | sheetId               | number                    | The sheet this span is on.                                        |
        | dimension             | enum (`Dimension`)        | The dimension of the span                                         |
        | startIndex            | number                    | The start (inclusive) of the span, or not set if unbounded.       |
        | endIndex              | number                    | The end (exclusive) of the span, or not set if unbounded.         |

        == valueInputOption ==
        ``valueInputOption`` determines how the input data should be interpreted.

        | =Options=                         | =Description=                                                                     |
        | INPUT_VALUE_OPTION_UNSPECIFIED    | Default input value. This value must not be used.                                 |
        | RAW                               | The values the user has entered will not be parsed and will be stored as-is.      |
        | USER_ENTERED                      | The values will be parsed as if the user typed them into the UI. Numbers will \
                                              stay as numbers, but strings may be converted to numbers,dates,etc. following \
                                              the same rules that are applied when entering text into a cell via the Google \
                                              Sheets UI.                                                                        |

        == InsertDataOption ==
        Determines how existing data is changed when new data is input.

        | =Enums=               |                                                                                               |
        | OVERWRITE             | The new data overwrites existing data in the areas it is written. (Note: adding data to \
                                  the end of the sheet will still insert new rows or columns so the data can be written.)       |
        | INSERT_ROWS           | Rows are inserted for the new data.                                                           |

        == ValueRange ==
        Data within a range of the spreadsheet.
         - json representation
        | {
        |   "range" :   string,
        |   "majorDimensions" : "ROWS",
        |   "values":   [
        |       array
        |   ]
        |  }

        | =Fields=         | =Input=                        | =Description=                                                     |
        | range            | string                         | The range the values cover, in A1 notation. For output, this  \
                                                              range indicates the entire requested range, even though the   \
                                                              values will exclude trailing rows and columns. When appending \
                                                              values, this field represents the range to search for a table,\
                                                              after which values will be appended.                              |
        | majorDimension   | enum (`Dimension`)             | The major dimension of the values. For output, if the         \
                                                              spreadsheet data is: A1=1,B1=2,A2=3,B2=4, then requesting     \
                                                              range=A1:B2,majorDimension=ROWS will return [[1,2],[3,4]],    \
                                                              whereas requesting range=A1:B2,majorDimension=COLUMNS will    \
                                                              return [[1,3],[2,4]].For input, with range=A1:B2,             \
                                                              majorDimension=ROWS then [[1,2],[3,4]] will set A1=1,B1=2,    \
                                                              A2=3,B2=4. With range=A1:B2,majorDimension=COLUMNS then       \
                                                              [[1,2],[3,4]] will set A1=1,B1=3,A2=2,B2=4. When writing, if  \
                                                              this field is not set, it defaults to ROWS.                       |
        | values[]          | array (`ListValue` format)    | The data that was read or to be written. This is an array of  \
                                                              arrays, the outer array representing all the data and each    \
                                                              inner array representing a major dimension. Each item in the  \
                                                              inner array corresponds with one cell. For output, empty      \
                                                              trailing rows and columns will not be included.For input,     \
                                                              supported value types are: bool, string, and double. Null     \
                                                              values will be skipped. To set a cell to an empty value, set  \
                                                                  the string value to an empty string.                          |

        == ListValue ==
        ``ListValue`` is a wrapper around a repeated field of values.

        The JSON representation for ``ListValue`` is JSON array.
        | =Field Name=              | =Type=                    | =Description=                                                 |
        | values                    | `Value`                   | Repeated field od dynamically typed values.                   |


        == Value ==
        ``Value`` represents a dynamically typed value which can be either null, a number, a string, a boolean, a recursive\
            struct value, or a list of values. A producer of value is expected to set one of that variants, absence of any \
                variant indicates an error.

        The JSON representation for ``Value`` is JSON value.

        | =Field Name=              | =Type=                | =Description=                                                     |
        | Union field, only one of the following                                                                                |
        | =null_value=              | NullValue             | Represents a null value.                                          |
        | =number_value=            | double                | Represents a double value.                                        |
        | =string_value=            | string                | Represents a string value.                                        |
        | =bool_value=              | bool                  | Represents a boolean value.                                       |
        | =struct_value=            | Struct                | Represents a structured value.                                    |
        | =list_value=              | ListValue             | Represents a repeated Value.                                      |

        == DataFilter ==
        Filter that describes what data should be selected or returned from a request.

         - JSON Representation
        | {
        |       // Union field filter can be only one of the following:
        |       "developerMetadataLookup": {
        |       object (DeveloperMetadataLookup)
        |       },
        |       "a1Range": string,
        |       "gridRange": {
        |       object (GridRange)
        |       }
        |       // End of list of possible types for union field filter.
        | }

        | =Fields=                      | =Input=                               | =Description=                                 |
        | Union field ``filter`` . The kinds of filters that may limit what data is selected. ``filter`` can only b\
            e one of the following                                                                                  |
        | =developerMetadataLookup=     | object(`DeveloperMetadataLookup`)     | Selects data associated with the \
            developer metadata matching the criteria described by this `DeveloperMetadataLookup`.                   |
        | =a1Range=                     | string                                | Selects data that matches the spe\
            cified A1 range.                                                                                        |
        | =gridRange=                   | object(`GridRange`)                   | Selects data that matches the ran\
            ge described by the GridRange.                                                                         |
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self,
                 scopes=['https://www.googleapis.com/auth/spreadsheets']):
        """Google Sheets API v4 requires that you set the scope to be used. Refer to the
           `OAuth 2.0 Scope Information for the Google Sheets API`. Multiple Scopes could be defined.
           The Scopes should be the one used in generating the `.pickle` file.
        """
        libraries = [
        ]
        HybridCore.__init__(self, libraries)
        self.SCOPES = scopes

    @keyword
    def initialize_spreadsheet(self, spreadsheetId,
                               tokenFile,):
        """Initializes the connection to the specified Google Spreadsheet. Takes 2 positional arguments\
            spreadsheetId and tokenFile.
           Sample Usage:
           | `Initialize Spreadsheet`   | 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms  | ${EXECDIR}/token.pickle   |
        """
        self.spreadsheetId = spreadsheetId
        self.tokenFile = tokenFile
        self.creds = self._validate_credentials()
        self.service = build('sheets', 'v4', credentials=self.creds, cache_discovery=False)
        self.sheet = self.service.spreadsheets()
        self.sheetObject = self.sheet.get(spreadsheetId=self.spreadsheetId).execute()
        self.sheetMap = self._create_prop_map()

    @keyword
    def duplicate_sheet(self, sheet_index, duplicate_sheet_name=None):
        """Duplicates a specified sheet to the current spreadsheet.

            Usage:
            | `Duplicate Sheet`         | sheet_id = 0 | sheet_name = New_Sheet1 |

            If successful, returns the index of the duplicated sheet.

            Uses `Copy Sheet To`, see `Copy Sheet To` for more details.
        """
        response = self.copy_sheet_to(sheet_index)
        self.rename_sheet(int(response['sheetId']), duplicate_sheet_name)
        return {
            'title': str(response['title']),
            'index': int(response['index']),
            'sheetId': response['sheetId']
        }

    @keyword
    def rename_sheet(self, sheet_id, new_sheet_name):
        """Renames a specified sheet to the current spreadsheet.

            Usage:
            | `Rename Sheet`            | sheet_id = 0 | sheet_name = New_Sheet1 |
        """
        return self.google_sheets_batch({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "title": new_sheet_name,
                },
                "fields": "title",
            }
        })

    @keyword
    def insert_column(self,
                      startIndex,
                      endIndex,
                      sheet_id=0,
                      inheritFromBefore=True
                      ):
        """Inserts an empty Column into the specified sheet, startIndex, endIndex.
        """
        return self._insert(dimension='COLUMNS',
                            sheet_id=sheet_id,
                            startIndex=startIndex,
                            endIndex=endIndex,
                            inheritFromBefore=inheritFromBefore
                            )

    @keyword
    def insert_row(self,
                   startIndex,
                   endIndex,
                   sheet_id=0,
                   inheritFromBefore=True
                   ):
        """Inserts an empty Row into the specified sheet, startIndex, and endIndex.
        """
        return self._insert(dimension='ROWS',
                            sheet_id=sheet_id,
                            startIndex=startIndex,
                            endIndex=endIndex,
                            inheritFromBefore=inheritFromBefore
                            )

    def _insert(self,
                dimension,
                sheet_id=0,
                **kwargs
                ):
        data = {
            'insertDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': dimension,
                    'startIndex': kwargs['startIndex'],
                    'endIndex': kwargs['endIndex']
                },
                'inheritFromBefore': kwargs['inheritFromBefore']
            }
        }
        return self.google_sheets_batch(data)

    @keyword
    def google_sheets_batch(self, requests):
        """Google Sheets API v4 batchUpdate.
        """
        requestBody = {
            'requests': requests
        }
        try:
            return self.sheet.batchUpdate(spreadsheetId=self.spreadsheetId,
                                          body=requestBody).execute()
        except Exception as err:
            raise err

    @keyword
    def copy_sheet_to(self, sheet_id, spreadsheet_id=None):
        """Copies the specified sheet to the current spreadsheet.

            Usage:
            | ${spreadsheet_id}          | Set Variable | YOURSPREADSHEETID                     |
            | `Copy Sheet To`            | sheet_id = 0 | spreadsheet_id = ${spreadsheet_id}    |
        """
        spreadsheet_id = self.spreadsheetId if spreadsheet_id is None else spreadsheet_id
        requestBody = {
            'destination_spreadsheet_id': str(spreadsheet_id),
        }
        try:
            response = self.sheet.sheets().copyTo(spreadsheetId=spreadsheet_id,
                                                  sheetId=sheet_id,
                                                  body=requestBody).execute()
            logger.console(response)
            return response
        except Exception as err:
            raise err

    @keyword
    def append_values(self, range_name, body,
                      insertDataOption='INSERT_ROWS',
                      valueInputOption='USER_ENTERED'):
        """ Appends data after a table of data in a sheet.

        The body of the update request must be a `ValueRange` object, though the only required field is
            values. If range is specified, it must match the range in the URL. In the ValueRange, you
                can optionally specify its majorDimension. By default, ROWS is used. If COLUMNS is
                    specified, each inner array is written to a column instead of a row.

        *NOTE*: The majorDimension parameter does not control if data is added as rows or columns to
            the table. Data will always be added to subsequent rows. The parameter only controls how
                the input data is read.

        The input ``range_name`` is used to search for existing data and find a "table" within that range.
        Values are appended to the next row of the table, starting with the first column of the table.
        For example, consider a sheet *Sheet1* that looks like:
        |       | =A=   | =B=   | =C=   | =D=   | =E=   |
        | =1=   | x     | y     | z     |       |       |
        | =2=   | x     | y     | z     |       |       |
        | =3=   |       |       |       |       |       |
        | =4=   |       | x     | y     |       |       |
        | =5=   |       |       | y     | z     |       |
        | =6=   |       | x     | y     | z     |       |
        | =7=   |       |       |       |       |       |

        There are two tables in the sheet: ``A1:C2``, and ``B4:D6``. Append values would begin at ``B7``
        for all the following ``range`` inputs:
            - ``Sheet1``, because it will examine all the data in the sheet, determine that the table at
                ``B4:D6`` is the last table.
            - ``B4`` or ``C5:D5``, because they're both in the ``B4:D6`` table.
            - ``B2:D4``, because the last table in the range is the ``B4:D6`` table (despite also containing
                the ``A1:C2`` table).
            - ``A3:G10``, because the last table in the range is the ``B4:D6`` table (despite starting before
                and ending after it).

        The following ``range`` inputs would not start writing at ``B7``:
            - ``A1`` would start writing at ``A3``, because that's in the ``A1:C2`` table.
            - ``E4`` would not start writing at ``E4``, because it's not in any table. (``A4`` would also start
                writing at ``A4`` for the same reasons.)

        Additionally, you can choose if you want to overwrite existing data after a table or insert new rows
        for the new data. By default, the input overwwrites data after the table. To write the new data
        into new rows, specify ``insertDataOption==INSERT_ROWS``.

        Refer to the `InsertDataOption` for the accepted arguments.
        """
        try:
            result = self.sheet.values().append(spreadsheetId=self.spreadsheetId,
                                                range=range_name,
                                                valueInputOption=valueInputOption,
                                                insertDataOption=insertDataOption,
                                                body=body).execute()
            return result
        except Exception as err:
            raise err

    @keyword
    def get_spreadsheet_id(self):
        """Returns the initialized spreadsheet ID.
        """
        if self.spreadsheetId:
            return self.spreadsheetId
        else:
            return "No Spreadsheet Initiated."

    @keyword
    def get_spreadsheet(self):
        """
        Returns the current initialized spreadsheet .  A spreadsheet Instance must be created first.
        """
        return self.sheetObject

    def _create_prop_map(self):
        map = {}
        for prop in self.sheetObject['sheets']:
            data = {}
            data['index'] = prop['properties']['index']
            data['sheetId'] = prop['properties']['sheetId']
            map[str(prop['properties']['title'])] = data
        logger.console(map)
        return map

    @keyword
    def get_sheet_index_by_sheet_name(self, sheetName):
        """
        Returns the sheet index of the given sheetName.

        Fails if the sheetName does not exist on the current sheet.
        """
        try:
            return self.sheetMap[sheetName]['index']
        except Exception as err:
            raise err

    @keyword
    def get_sheet_id_by_sheet_name(self, sheetName):
        """
        Returns the sheet index of the given sheetName.

        Fails if the sheetName does not exist on the current sheet.
        """
        try:
            return self.sheetMap[sheetName]['sheetId']
        except Exception as err:
            raise err

    def _validate_credentials(self):
        """ The file token.pickle stores the user's access and refresh
            tokens, and is created automatically when the authorization
            flow completes for the first
            time.
        """
        creds = None
        if os.path.exists(self.tokenFile):
            with open(self.tokenFile, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds

    @keyword
    def fetch_single_range(self, range_name, majorDimension='ROWS',
                           valueRenderOption='FORMATTED_VALUE'):
        """Fetches data from the initialized spreadsheet given the range.
            Example:
            | `Fetch Single Range`        | Sheets1!A1:D |
        """
        try:
            values = self.sheet.values().get(spreadsheetId=self.spreadsheetId,
                                             majorDimension=majorDimension,
                                             valueRenderOption=valueRenderOption,
                                             range=range_name).execute()
            return values
        except Exception as err:
            raise err

    @keyword
    def fetch_multiple_range(self, ranges, majorDimension='ROWS',
                             valueRenderOption='FORMATTED_VALUE'):
        """Fetches the Specified Spreadsheet range/s. Given range could be single or multiple,
           though it is more correct to just use `Fetch Single Range` if the range parameter is just
           a single range. Multiple range parameters should be passed as a list type.

           Example:
           | `Fetch Multiple Range`     | ${ranges}                 |                           |
           | ${data}                    | `Fetch Multiple Range`    |  ${range_list}            |

        """
        try:
            values = self.sheet.values().batchGet(spreadsheetId=self.spreadsheetId,
                                                  majorDimension=majorDimension,
                                                  valueRenderOption=valueRenderOption,
                                                  ranges=ranges).execute()
            return values
        except Exception as err:
            raise err

    @keyword
    def write_to_range(self, ranges, body,
                       valueInputOption='USER_ENTERED'):
        """The body of the update request must be a `ValueRange object`, though the only required field is
           values. If range is specified, it must match the range in the URL. In the ValueRange, you can
           optionally specify its majorDimension. By default, ROWS is used. If COLUMNS is specified,
           each inner array is written to a column instead of a row.

           When updating, values with no data are skipped. To clear data, use an empty string ("").
        """
        try:
            result = self.sheet.values().update(spreadsheetId=self.spreadsheetId,
                                                range=ranges,
                                                valueInputOption=valueInputOption,
                                                body=body).execute()
            return result
        except Exception as err:
            raise err

    @keyword
    def write_to_multiple_range(self, data,
                                valueInputOption='USER_ENTERED',
                                majorDimension='ROWS'):
        """Write to multiple discontinuous ranges. For writing to single defined range,
           use `Write To Range`.
        """
        body = {
            'valueInputOption': valueInputOption,
            'data': data
        }
        try:
            result = self.sheet.values().batchUpdate(spreadsheetId=self.spreadsheetId,
                                                     body=body).execute()
            return result
        except Exception as err:
            raise err
