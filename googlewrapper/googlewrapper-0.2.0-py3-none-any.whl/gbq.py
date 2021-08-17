from google.cloud import bigquery
from .connect import Connection
import pandas as pd
from datetime import date

class GoogleBigQuery:
    """
    Google API Wrapper for Google Big Query
    REMEMBER your 'gba-sa.json' file in your PATH
    This is different from the 'client_secret.json'

    Parameters
    auth: googleapiclient.discovery.Resource object 
            created from the Connection class by default
            no need to mess with this
    """
    def __init__(self, auth = Connection().gbq()):
        self._client = bigquery.Client(credentials=auth)
        self._project = auth.project_id
        self._dataset = None
        self._table = None

    def set_dataset(self, dataset_name:str) -> None:
        """
        Assigns the active dataset name
        """
        self._dataset = dataset_name

    def set_table(self, table_name:str) -> None:
        """
        Assigns the active GBQ table name
        """
        self._table = table_name

    def full_table_name(self) -> str:
        """
        Combines self._dataset and self._table
        this becomes the full table name in GBQ

        Returns this combination as a string
        """
        return f"{self._dataset}.{self._table}"

    def list_datasets(self) -> list:
        """
        returns a list of all dataset ids/names in the authorized client
        """
        return [x.dataset_id for x in list(self._client.list_datasets())]

    def send(
            self, 
            df:pd.DataFrame, 
            chunk_size:int = 10000, 
            behavior:str = "append", 
            progress_bar:bool = False
            ) -> None:
        """
        sends the df parameter into the active GBQ table & dataset
        
        Change chunk size using the chunk_size variable, 
        the default is set to 10,000
        
        if table already exists you state the behavior you'd like to see
        append: add to bottom of table 
        fail: fail, no import happens
        replace: drop the table, insert current df
        
        for a visual progress bar in the terminal
        pass in progresss_bar = True
        """
        try:
            df.to_gbq(
                destination_table=f"{self._dataset}.{self._table}",
                project_id=self._project,
                chunksize=chunk_size,
                if_exists=behavior,
                progress_bar=progress_bar,
            )
        except AttributeError as e:
            issue = e.args[0].split("'")[-2].replace("_", "")
            raise AttributeError(
                f"Please run self.set_{issue}"
                f"('your_{issue}_name_here') before running self.send()"
            )

    def read(self, query_string:str) -> pd.DataFrame:
        """
        Read from GBQ using a query string

        Returns a pd.DataFrame
        """
        df = pd.read_gbq(
                query = query_string,               
                project_id = self._project,
                progress_bar = "None"
                )
        return df

    def delete_day(self, date_to_delete:date, str_return:bool = False):
        """
        deletes the passed in day from the
        pre-determined table in GBQ
        """
        query_string = f"""
        DELETE
        FROM `{self._project}.{self._dataset}.{self._table}`
        WHERE
        EXTRACT(Year FROM `Date`) = {date_to_delete.year}
        AND
        EXTRACT(Month FROM `Date`) = {date_to_delete.month}
        AND
        EXTRACT(Day FROM `Date`) = {date_to_delete.day}
        """

        if str_return:
            return query_string
            
        return self._client.query(query_string)
