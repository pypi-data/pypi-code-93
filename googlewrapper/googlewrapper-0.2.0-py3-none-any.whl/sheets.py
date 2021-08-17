from .connect import Connection
from pandas import DataFrame


class GoogleSheets:
    """
    Google API Wrapper for Google Sheets
    REMEMBER your 'client_secret.json' file in your PATH

    Parameters
    url: string of Google Sheet URL
    auth: googleapiclient.discovery.Resource object 
            created from the Connection class by default
            no need to mess with this

    Uses the pygsheets library
    https://pygsheets.readthedocs.io/en/stable/index.html
    """
    def __init__(self, url:str, auth = Connection().pygsheets()):
        self.url = url
        self.id = self.__get_id()
        self.auth = auth
        self.wb = self.auth.open_by_url(self.url)
        self.sheet = self.wb.sheet1

    def __get_id(self) -> str:
        """
        extracts the sheet id from the passed in URL
        """
        return self.url.split('d/')[1].split('/edit')[0]

    def set_sheet(self, sheet_name:str) -> None:
        """
        set the active sheet to sheet_name
        """
        self.sheet = self.wb.worksheet('title',sheet_name)

    # Spreadsheet/Tab Methods
    def df(self,start:str = 'a1', index:int = 1) -> DataFrame:
        """
        gets the contents of the sheet, and returns it as a pd DataFrame

        https://pygsheets.readthedocs.io/en/stable/worksheet.html#pygsheets.Worksheet.get_as_df
        """
        try:
            return self.sheet.get_as_df(start=start,index_column=index)
        except AttributeError:
            raise AttributeError('Please declare your sheet name using .set_sheet(name)')

    def save(
            self, 
            df:DataFrame, 
            start:str = 'a1', 
            index:bool = True, 
            header:bool = True, 
            extend:bool = True
            ) -> None:
        """
        Saves a pandas DataFrame to the active sheet
        """
        if isinstance(df,DataFrame):
            self.sheet.set_dataframe(df,start,copy_index=index,copy_head=header,extend=extend)
        else:
            raise TypeError("Please pass in a pd.DataFrame to save to Google Sheets")

    def clear(self,start:str = 'a1', end:str = None) -> None:
        """
        clears the contents of a worksheet

        both parameters are in 'a1' notation
        start: starting cell to clear contents
                defaults to 'a1'
        end: ending cell to clear contents (defaults to None)
                defaults to None (will clear entire worksheet)

        """
        self.sheet.clear(start,end)

    def row(self,row_number:int) -> list:
        """
        returns a list containing the row values

        accepts row_number that corresponds 
        to the row in the active sheet
        """
        return self.sheet.get_row(row_number,include_tailing_empty=False)

    def col(self,col_number:int) -> list:
        """
        returns a list containing the column values

        accepts col_number that corresponds 
        to the col in the active sheet
            A = 1
            B = 2
            etc.
        """
        return self.sheet.get_col(col_number,include_tailing_empty=False)
        
    # Entire Workbook Methods
    def add_sheet(self, sheet_name:str, data:DataFrame = None) -> None:
        """
        add a tab named sheet_name to your workbook

        you can pass in a pandas dataframe and that will be 
        inserted into starting cell a1
        """
        self.wb.add_worksheet(sheet_name)
        self.set_sheet(sheet_name)
        if data is not None:
            self.save(data)

    def delete_sheet(self, sheet_name:str) -> None:
        """
        delete a tab named sheet_name from your workbook
        """
        self.wb.del_worksheet(sheet_name)

    def share(
                self, 
                email_list:list, 
                role:str = 'reader', 
                role_type:str = 'user'
                ) -> None:
        """
        shares the active sheet with all the emails in the email_list

        assigns the permissions as declared by the role variable
        ['organizer', 'owner', 'writer', 'commenter', 'reader']
        default: reader

        role_type
        ['user', 'group', 'domain', 'anyone']
        default: user

        example on how to share with anyone
        self.share([],role='reader', type='anyone')
        """
        if not email_list:
            self.wb.share('', role, role_type)
        else:
            for email in email_list:
                self.wb.share(email, role, role_type)
