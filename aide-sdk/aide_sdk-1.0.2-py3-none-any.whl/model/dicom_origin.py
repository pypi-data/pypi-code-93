import abc
import dataclasses
import os
from typing import Dict, Optional, List

from aide_sdk.model.origin import Origin
from aide_sdk.model.dicom_series import DicomSeries
from aide_sdk.utils.helpers import clean_path


@dataclasses.dataclass
class DicomStudy(abc.ABC):
    study_uid: str
    file_path: str
    _series: List[Dict]
    _series_objects: List[DicomSeries] = dataclasses.field(init=False, default=None)

    def get_series_by_id(self, series_id: str) -> Optional[DicomSeries]:
        for x in self.series:
            if x.series_id == series_id:
                return x

    @property
    def series(self):
        if not self._series_objects:
            self._series_objects = []
            for x in self._series:
                series_id = x.get('SeriesInstanceUID')
                series_folder = clean_path(series_id)
                series_path = os.path.join(self.file_path, series_folder)
                self._series_objects.append(DicomSeries(series_id, series_path, x))
        return self._series_objects

    def has_series(self, series_id):
        return self.get_series_by_id(series_id) is not None


@dataclasses.dataclass
class DicomOrigin(Origin, DicomStudy):
    pass
