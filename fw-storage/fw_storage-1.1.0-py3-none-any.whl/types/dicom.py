"""DICOM storage module."""
import re
import tempfile
import typing as t
from pathlib import Path

import pydicom
from fw_utils import Filters, fileglob
from pydicom.dataset import Dataset, FileMetaDataset
from pynetdicom import AE, StoragePresentationContexts, build_role, evt, sop_class

from ..fileinfo import FileInfo
from ..storage import AnyPath, DicomBaseStorage

__all__ = ["DICOM"]

PENDING = {0xFF00, 0xFF01}
SUCCESS = 0x0000

# pylint: disable=no-member
STUDY_FIND = sop_class.StudyRootQueryRetrieveInformationModelFind
STUDY_GET = sop_class.StudyRootQueryRetrieveInformationModelGet
STUDY_MOVE = sop_class.StudyRootQueryRetrieveInformationModelMove
# pylint: enable=no-member


class DICOM(DicomBaseStorage):
    """Storage class for medical imaging."""

    url_re = re.compile(
        r"dicom://"
        r"((?P<aet>[^:@]+)(:(?P<rport>[^@]\d+))?@)?"
        r"(?P<host>[^:]+):(?P<port>\d+)"
        r"(/(?P<aec>.+))?"
    )

    def __init__(
        self,
        host: str,
        port: str,
        aec: t.Optional[str] = None,
        aet: str = "FW-STORAGE",
        rport: t.Optional[str] = None,
    ) -> None:
        """Construct DICOM storage.

        Args:
            host: DICOM SCP / PACS server host or IP.
            port: DICOM SCP / PACS server port.
            aec: Called Application Entity Title.
            aet: Calling Application Entity Title.
            rport: Return port for moving images (C-MOVE).
        """
        # pylint: disable=too-many-arguments
        self.ae = AE(ae_title=aet.encode())
        # Add required contexts for operations
        contexts = [STUDY_FIND, STUDY_GET, STUDY_MOVE]
        for cx in contexts:
            self.ae.add_requested_context(cx)

        for cx in StoragePresentationContexts:
            if len(self.ae.requested_contexts) == 128:
                break
            self.ae.add_requested_context(cx.abstract_syntax)

        # Both scu and scp roles needs to be set to True so most C service can be
        # supported. Most C services require SCU role for successful association.
        # C-GET requires to act as an SCP to handle responses.
        roles = [
            build_role(cx.abstract_syntax, scp_role=True, scu_role=True)
            for cx in StoragePresentationContexts
        ]

        self.rport = int(rport) if rport else None
        self.storage_scp = None
        self.assoc = self.ae.associate(
            host,
            int(port),
            ae_title=aec or b"ANY-SCP",
            ext_neg=roles,
            evt_handlers=handlers,
        )

    def start_storage_scp(self):
        """Start Storage SCP to handle C-MOVE responses."""
        if not self.rport:
            msg = "Initiate DICOM Storage with DICOM url that includes return port"
            raise ValueError(msg)
        # Initialise the Application Entity
        ae = AE()

        # Add a requested presentation context
        ae.add_requested_context(STUDY_MOVE)

        # Add the Storage SCP's supported presentation contexts
        ae.supported_contexts = StoragePresentationContexts
        # Start our Storage SCP in non-blocking mode, listening on port self,rport
        ae.ae_title = self.ae.ae_title
        self.storage_scp = ae.start_server(
            ("", self.rport), block=False, evt_handlers=handlers
        )

    def cleanup(self):
        """Stop storage_scp if running and abort association."""
        if self.storage_scp:
            self.storage_scp.server_close()
            self.storage_scp = None
        if not self.assoc.is_aborted:
            self.assoc.abort()

    def ls(
        self, path: str = "", *, include: Filters = None, exclude: Filters = None, **_
    ) -> t.Iterator[FileInfo]:
        """Yield items under path that match the include/exclude filters."""
        ds = Dataset()
        ds.QueryRetrieveLevel = "SERIES"
        ds.SeriesInstanceUID = None
        ds.SeriesDate = None
        ds.SeriesTime = None
        ds.NumberOfSeriesRelatedInstances = None
        study_uid, series_uid = self.apply_path_re(self.PATH_RE_OPTIONAL, path)
        if include:
            parse_filters_to_ds(include, ds)
        exc_filters = {}
        if exclude:
            exc_filters = self.parse_filters_to_dict(exclude)
            for key in exc_filters:
                self.param_to_tag(key)
                setattr(ds, key, None)
        study_uids = [study_uid] if study_uid else self._get_every_study_uid()
        # TODO: Series level ls might be unnecessary, see stat method
        if series_uid:
            ds.SeriesInstanceUID = series_uid
        ds.StudyInstanceUID = study_uids
        responses = self.assoc.send_c_find(ds, STUDY_FIND)
        for resp in iter_scp_responses(responses, exc_filters):
            yield self.result_to_fileinfo(resp)

    def get(self, path: AnyPath, **kwargs: t.Any) -> AnyPath:
        """Return a file opened for reading in binary mode."""
        s_path = self.abspath(path)
        study_uid, series_uid = self.apply_path_re(self.PATH_RE_REQUIRED, s_path)
        ds = Dataset()
        ds.QueryRetrieveLevel = "SERIES"
        ds.StudyInstanceUID = study_uid
        ds.SeriesInstanceUID = series_uid

        tmp = Path(tempfile.gettempdir()) / s_path
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            list(iter_scp_responses(self.assoc.send_c_get(ds, STUDY_GET)))
        except ValueError:
            self.start_storage_scp()
            responses = self.assoc.send_c_move(ds, self.ae.ae_title, STUDY_MOVE)
            list(iter_scp_responses(responses))
        return str(tmp)

    def set(self, file: AnyPath) -> None:  # type: ignore
        """Write a file at the given path in storage."""
        path = Path(self.abspath(file))
        paths = fileglob(path) if path.is_dir() else [path]
        for path in paths:
            ds = pydicom.dcmread(path)
            self.assoc.send_c_store(ds)

    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove file from storage."""
        raise NotImplementedError

    def stat(self, path: str) -> FileInfo:
        """Return FileInfo for a single series."""
        study_uid, series_uid = self.apply_path_re(self.PATH_RE_REQUIRED, path)
        ds = Dataset()
        ds.QueryRetrieveLevel = "SERIES"
        ds.SeriesInstanceUID = None
        ds.SeriesDate = None
        ds.SeriesTime = None
        ds.NumberOfSeriesRelatedInstances = None
        ds.SeriesInstanceUID = series_uid
        ds.StudyInstanceUID = study_uid
        responses = self.assoc.send_c_find(ds, STUDY_FIND)
        results = list(iter_scp_responses(responses))
        if len(results) == 1:
            return self.result_to_fileinfo(results[0])
        raise ValueError("Ambiguous resource or resource not found")

    def get_image_count(self, study_uid: str, series_uid: str) -> int:
        """Get image count of a series."""
        query_ds = Dataset()
        query_ds.QueryRetrieveLevel = "IMAGE"
        query_ds.StudyInstanceUID = study_uid
        query_ds.SeriesInstanceUID = series_uid
        query_ds.SOPInstanceUID = ""
        responses = self.assoc.send_c_find(query_ds, STUDY_FIND)
        return len(list(iter_scp_responses(responses)))

    def _get_every_study_uid(self):
        """Get every study uid."""
        study_uids = []
        study_ds = Dataset()
        study_ds.QueryRetrieveLevel = "STUDY"
        study_ds.StudyInstanceUID = None
        for resp in iter_scp_responses(self.assoc.send_c_find(study_ds, STUDY_FIND)):
            study_uids.append(resp.StudyInstanceUID)
        return study_uids


def handle_store(event):
    """Handle a C-STORE request event."""
    ds = event.dataset
    ds.file_meta = FileMetaDataset(event.file_meta)

    tmp = (
        Path(tempfile.gettempdir())
        / str(ds.StudyInstanceUID)
        / str(ds.SeriesInstanceUID)
    )
    tmp.mkdir(parents=True, exist_ok=True)
    # Save the dataset using the SOP Instance UID as the filename
    ds.save_as(f"{tmp}/{ds.SOPInstanceUID}.dcm", write_like_original=False)

    # Return a 'Success' status
    return SUCCESS


handlers = [(evt.EVT_C_STORE, handle_store)]


def iter_scp_responses(
    responses: t.Iterator[t.Tuple[Dataset, Dataset]],
    exc_filters: t.Optional[dict] = None,
) -> t.Iterator[Dataset]:
    """Process responses sent by the SCP."""
    for status, identifier in responses:
        if not status:
            msg = "Connection error: timed out, aborted or received invalid response"
            raise ValueError(msg)
        if status.Status in PENDING:
            if exc_filters:
                if DicomBaseStorage.apply_exclude_filters(identifier, exc_filters):
                    continue
            yield identifier
        elif status.Status == SUCCESS:
            return
        else:
            raise ValueError(f"An error occured (DIMSE status: {status})")


def parse_filters_to_ds(filters: t.List[str], ds: Dataset) -> None:
    """Parse list of strings into Dataset filters."""
    for filt in filters:
        try:
            key, value = filt.split("=", maxsplit=1)
            if "," in value:
                setattr(ds, key, value.split(","))
            else:
                setattr(ds, key, value)
        except ValueError as exc:
            raise ValueError("Missing filter key or value") from exc
