import json
from typing import Any, Dict, List

import requests
from uplink import Body, Consumer, Path, get, headers, post, put, returns

from .models import NameSpaces, TableRow, Tables, _TableRow
from .utils import to_base64


class HBase(Consumer):
    """A Python Client for the HBase API.
    """

    def __init__(self, **kwargs):
        session = requests.Session()
        session.verify = False
        super().__init__(client=session, **kwargs)

    @headers({"Accept": "text/xml", "Content-Type": "text/xml"})
    @post("{table}/schema")
    def __create_table(self, table: Path, schema: Body) -> requests.request:
        """Creates a table on HBase
        curl "{host}/{table}/schema" -X POST -d '<?xml version="1.0" encoding="UTF-8"?><TableSchema name="users"><ColumnSchema name="cf" /></TableSchema>' -H "Accept: application/json" -H "Content-Type: application/json" 
        """
        ...

    @headers({"Accept": "application/json", "Content-Type": "application/json"})
    @put("{table}/{row_id}")
    def __insert_row(self, table: Path, row_id: Path, data: Body) -> requests.request:
        """Inserts a row into the given table
        curl "{host}/{table}/{row_id}" -X PUT -d "{\"Row\":[{\"key\":\"cm93MTA=\", \"Cell\": [{\"column\":\"Y2Y6ZQ==\", \"$\":\"Q2hyaXM=\"}]}]}" -H "Accept: text/json" -H "Content-Type: application/json" 
        """
        ...

    @returns.json(_TableRow)
    @headers({"Accept": "application/json"})
    @get("{table}/{row_id}")
    def __get_row(self, table: Path, row_id: Path) -> _TableRow:
        """Gets a given row from the given table
        curl "{host}/{table}/{row_id}" -H "Accept: text/xml" 
        """
        ...

    @returns.json(_TableRow)
    @headers({"Accept": "application/json"})
    @get("{table}/{row_id}/{column}:e/{timestamp}")
    def __get_row_with_timestamp(self, table: Path, row_id: Path, column: Path, timestamp: Path) -> _TableRow:
        """Gets a given row from the given table for the specified timestamp
        curl "{host}/{table}/{row_id}/{column}:e/{timestamp}" -H "Accept: text/xml" 
        """
        ...

    @headers({"Accept": "application/json"})
    @post("namespaces/{namespace}")
    def create_namespace(self, namespace: Path) -> requests.request:
        """Creates a namespace
        curl "{host}/namespaces/{namespace}" -X POST -H "Accept: application/json" 
        """
        ...

    @returns.json(Tables)
    @headers({"Accept": "application/json"})
    @get("namespaces/{namespace}/tables")
    def list_tables(self, namespace: Path = "default") -> Tables:
        """Lists all tables under a namespace
        curl "{host}/namespaces/{namespace}/tables" -H "Accept: text/xml"
        """
        ...

    @returns.json(NameSpaces)
    @headers({"Accept": "application/json"})
    @get("namespaces")
    def list_namespaces(self) -> NameSpaces:
        """Lists all namespaces
        curl "{host}/namespaces" -H "Accept: text/xml"
        """
        ...

    def get_row(self, table: str, row_id: str) -> TableRow:
        """Gets a given row from the given table and decodes it from base64 for convenience
        """
        return self.__get_row(table, row_id).from_base64()

    def get_row_with_timestamp(self, table: str, row_id: str, column: str, timestamp: str) -> TableRow:
        """Gets a given row from the given table with a specified timestamp and decodes it from base64 for convenience
        """
        return self.__get_row_with_timestamp(table, row_id, column, timestamp).from_base64()

    def create_table(self, table: str, column_names: List[str]) -> requests.request:
        """Utility function for creating a table - HBase REST API only accepts XML for this request"""
        xml_packet = f"""<?xml version="1.0" encoding="UTF-8"?><TableSchema name="{table}">{''.join(f'<ColumnSchema name="{col}" />' for col in column_names)}</TableSchema>"""
        return self.__create_table(table, xml_packet)

    def insert_row(self, table: str, row_id: str, data: Dict[str, Any]) -> requests.request:
        """Utility function for inserting a row into a table, as the HBase REST API needs the data encoded into base64"""
        packet = {
            "Row": [
                {
                    "key": to_base64(row_id),
                    "Cell": [{"column": to_base64(f"{k}:e"), "$": to_base64(v)} for k, v in data.items()],
                }
            ]
        }
        return self.__insert_row(table, row_id, data=json.dumps(packet))
