from typing import List, Type
from uuid import uuid4
import pathlib
from datetime import datetime

from .models.output_structure import (
    DataPoint,
    Meta,
    Series,
    Table,
    TableRow,
    Tag,
    UploadStructure
)


class LocalStorage:
    STORAGE_PATH = None

    def __init__(self) -> None:
        self._time_prefix = datetime.now().isoformat(timespec='seconds').replace(':', '-')
        self._storage_path = (self.STORAGE_PATH or pathlib.Path.cwd()) / self._time_prefix

    def save_results(self, results: str, *args) -> str:
        self._storage_path.mkdir(parents=True, exist_ok=True)
        path = self._storage_path / f'{uuid4()}.json'
        with path.open('w') as f:
            f.write(results)
        return path


class Context:
    class models:
        series: Type[Series] = Series
        data_value: Type[DataPoint] = DataPoint
        table: Type[Table] = Table
        table_row: Type[TableRow] = TableRow
        tag: Type[Tag] = Tag

    def __init__(self, namespace, source_id, task_id):
        self.namespace = namespace
        self.source_id = source_id
        self.task_id = task_id
        self.producer = 'PWBM SP Local Toolset'

        self.series_ids = set()

        self.local_storage = LocalStorage()

    @classmethod
    def create_local(cls):
        return cls(task_id=0, source_id=0, namespace='test_namespace')

    def save_results(self, series: List[models.series], tables: List[models.table]) -> str:
        self._collect_series_ids(series)

        upload_structure = self._build_upload_structure(series, tables)
        payload = upload_structure.json(indent=2)

        return self.local_storage.save_results(
            payload,
            self.task_id,
            self.source_id,
            self.namespace,
        )

    def validate_results(self, series: List[models.series], tables: List[models.table]):
        self._build_upload_structure(series, tables)

    def _build_upload_structure(
            self,
            series: List[models.series],
            tables: List[models.table]
    ) -> UploadStructure:
        return UploadStructure(
            file_meta=Meta(
                producer=self.producer,
                namespace=self.namespace,
                task_id=self.task_id,
            ),
            tables=tables,
            series=series,
        )

    def _collect_series_ids(self, series: List[models.series]) -> None:
        for item in series:
            if series_id := item.correlation_id:
                self.series_ids.add(series_id)
