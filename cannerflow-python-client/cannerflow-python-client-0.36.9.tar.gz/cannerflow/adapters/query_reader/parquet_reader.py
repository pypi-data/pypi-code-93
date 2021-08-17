from dataclasses import dataclass
import pandas as pd
import requests
from io import BytesIO
from typing import List, Any
from cannerflow.request import CannerRequest
from cannerflow.logging import *


@dataclass
class ParquetQueryResult(object):
    columns: List[Any]
    data: Any


class ParquetQueryReader(object):
    def __init__(
        self,
        query_id: str,
        workspace_id: str,
        request: CannerRequest,
    ) -> None:

        self._query_id = query_id
        self._workspace_id = workspace_id
        self._request = request
        self._engine = "fastparquet"
        self._storage_urls = self.__retrieve_storage_urls()

    def read(self, limit: int, offset: int) -> ParquetQueryResult:
        # The columns is from parquet read
        query_columns = []
        self.__check_nested_collection_and_warning()
        if len(self._storage_urls) == 0:
            df = pd.DataFrame({})
        else:
            collected_dfs = []
            collected_count = 0
            for url in self._storage_urls:
                url_df = self.__get_pd_by_parquet_file(url, self._engine)
                collected_count += url_df.shape[0]
                collected_dfs.append(url_df)
                # if we get enough data, stop getting the next url dataframes
                if collected_count >= limit + offset:
                    break
            # concat collected dataframes from urls
            df = pd.concat(collected_dfs)
            query_columns = list(map(lambda column: {"name": column}, list(df.columns)))
        result = df.iloc[offset : limit + offset, :].to_numpy().tolist()
        # if query_columns is [] means, not storage url (no data)
        return ParquetQueryResult(query_columns, result)

    def __retrieve_storage_urls(self) -> List[str]:
        path_url = f"api/v1/query/{self._query_id}/result/signedUrls?workspaceId={self._workspace_id}"
        return self._request.get(path_url).get("signedUrls")

    def __get_pd_by_parquet_file(self, url, engine):
        r = requests.get(url)
        return pd.read_parquet(BytesIO(r.content), engine=engine)

    def __check_nested_collection_and_warning(self):
        result = self._request.get(
            f"api/v1/query/{self._query_id}?workspaceId={self._workspace_id}"
        )
        columns = result["columns"]
        logger = get_logger("Query", log_level=logging.WARNING)
        for column in columns:
            if self.__is_collection(column["typeSignature"]["rawType"]):
                for eleColumn in column["typeSignature"]["arguments"]:
                    if eleColumn["kind"] == "TYPE":
                        if self.__is_collection(eleColumn["value"]["rawType"]):
                            logger.warning(
                                f"Nested Collection isn't supported in fetchBy-storage-mode. Column %s: %s "
                                f"would be None.",
                                column["name"],
                                column["type"],
                            )
                    elif eleColumn["kind"] == "NAMED_TYPE":
                        if self.__is_collection(
                            eleColumn["value"]["typeSignature"]["rawType"]
                        ):
                            logger.warning(
                                f"Nested Collection isn't supported in fetchBy-storage-mode. Column %s: %s "
                                f"would be None.",
                                column["name"],
                                column["type"],
                            )

    def __is_collection(self, type):
        if ["array", "map", "row"].__contains__(type):
            return True
        return False
