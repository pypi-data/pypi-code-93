# Copyright 2019 Cognite AS
import logging
import os
import sys
import time
from collections import namedtuple

import deprecation
import grpc
from grpc._channel import (
    _InactiveRpcError,
    _SingleThreadedUnaryStreamMultiCallable,
    _StreamStreamMultiCallable,
    _UnaryStreamMultiCallable,
    _UnaryUnaryMultiCallable,
)

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic._api.file import FileAPI
    from cognite.seismic._api.file_seismic import FileSeismicAPI
    from cognite.seismic._api.job import JobAPI
    from cognite.seismic._api.partition import PartitionAPI
    from cognite.seismic._api.seismics import SeismicAPI
    from cognite.seismic._api.seismicstores import SeismicStoreAPI
    from cognite.seismic._api.slice import SliceAPI
    from cognite.seismic._api.slab import SlabAPI
    from cognite.seismic._api.survey import SurveyAPI
    from cognite.seismic._api.survey_v1 import SurveyV1API
    from cognite.seismic._api.time_slice import TimeSliceAPI
    from cognite.seismic._api.trace import TraceAPI
    from cognite.seismic._api.volume import VolumeAPI
    from cognite.seismic._api.volume_seismic import VolumeSeismicAPI
    from cognite.seismic.data_classes.errors import SeismicServiceError, _from_grpc_error
    from cognite.seismic.protos import ingest_service_pb2_grpc as ingest_serv
    from cognite.seismic.protos import query_service_pb2_grpc as query_serv
    from cognite.seismic.protos.v1 import seismic_service_pb2_grpc as seismic_serv

# The maximum number of retries
_MAX_RETRIES_BY_CODE = {
    grpc.StatusCode.INTERNAL: 1,
    grpc.StatusCode.ABORTED: 3,
    grpc.StatusCode.UNAVAILABLE: 5,
    grpc.StatusCode.DEADLINE_EXCEEDED: 5,
}

# The minimum seconds (float) of sleeping
_MIN_SLEEPING = 0.1
_MAX_SLEEPING = 5.0

logger = logging.getLogger(__name__)


def with_retry(f, transactional=False):
    def wraps(*args, **kwargs):
        retries = 0
        while True:
            try:
                return f(*args, **kwargs)
            except _InactiveRpcError as e:
                code = e.code()

                max_retries = _MAX_RETRIES_BY_CODE.get(code)
                if max_retries is None or transactional and code == grpc.StatusCode.ABORTED:
                    raise

                if retries > max_retries:
                    e = SeismicServiceError()
                    e.status = grpc.StatusCode.UNAVAILABLE
                    e.message = "maximum number of retries exceeded"
                    raise e

                backoff = min(_MIN_SLEEPING * 2 ** retries, _MAX_SLEEPING)
                logger.info("sleeping %r for %r before retrying failed request...", backoff, code)

                retries += 1
                time.sleep(backoff)

    return wraps


def decorate_with_retries(*args):
    for obj in args:
        for key, attr in obj.__dict__.items():
            if (
                isinstance(attr, _UnaryUnaryMultiCallable)
                or isinstance(attr, _StreamStreamMultiCallable)
                or isinstance(attr, _UnaryStreamMultiCallable)
                or isinstance(attr, _SingleThreadedUnaryStreamMultiCallable)
            ):
                setattr(obj, key, with_retry(attr))


def with_wrapped_rpc_errors(f):
    def wraps(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except _InactiveRpcError as e:
            raise _from_grpc_error(e) from None

    return wraps


def decorate_with_wrapped_rpc_errors(*args):
    for obj in args:
        for key, attr in obj.__dict__.items():
            setattr(obj, key, with_wrapped_rpc_errors(attr))


ParsedUrl = namedtuple("ParsedUrl", "is_insecure target")


def parse_url_parameter(url) -> ParsedUrl:
    """Parse a provided url, setting the secure/insecure status and standardizing the URL with a port
    """
    from urllib.parse import urlparse

    o = urlparse(url)
    # Urllib parsing quirk: if there's no schema, it parses the entire url as a path
    if o.netloc:
        netloc = o.netloc
    else:
        netloc = o.path

    scheme = o.scheme or "https"
    # We're removing any potential port that might exist, esp since it's also provided separately.
    # The rest of the URL (the path and params) are discarded
    base_url = netloc.split(":")[0] or "api.cognitedata.com"
    port = o.port or 443
    full_url = f"{base_url}:{port}"

    return ParsedUrl(scheme == "http", full_url)


class CogniteSeismicClient:
    """
    Main class for the seismic client
    """

    def __init__(
        self,
        api_key=None,
        base_url=None,
        port=None,
        custom_root_cert=None,
        *,
        insecure=False,
        project=None,
        no_retries=False,
        max_message_size_MB=10,
    ):
        # configure env
        self.api_key = api_key or os.getenv("COGNITE_API_KEY")
        self.project = project or os.getenv("COGNITE_PROJECT")

        if self.api_key is None or self.api_key == "":
            raise ValueError(
                "You have either not passed an api key or not set the COGNITE_API_KEY environment variable."
            )

        if port is not None or insecure:
            logger.warning("The port and insecure params are deprecated. Please include them in the base_url.")

        if base_url is not None:
            parsed_url = parse_url_parameter(base_url)
            self.target = parsed_url.target
            self.is_insecure = parsed_url.is_insecure
        else:
            self.target = "api.cognitedata.com:443"
            self.is_insecure = False

        self.metadata = [("api-key", self.api_key)]

        if self.project is not None:
            self.metadata.append(("cdf-project-name", self.project))
        else:
            logger.warning(
                "Undefined project name is deprecated behaviour. Please set the project name with CogniteSeismicClient(project='') or with environment variable COGNITE_PROJECT=''"
            )

        if max_message_size_MB > 10:
            logger.warning(
                "Raising the maximum message size above the default of 10MB may result in significant performance costs"
            )
        elif max_message_size_MB < 10:
            raise ValueError("Maximum message size must be at least 10MB")

        # start the connection
        options = [
            ("grpc.max_receive_message_length", max_message_size_MB * 1024 * 1024),
            ("grpc.keepalive_time_ms", 5000),
            ("grpc.keepalive_permit_without_calls", 1),
            ("grpc.http2.max_pings_without_data", 0),
            ("grpc.http2.min_time_between_pings_ms", 5000),
        ]
        if self.is_insecure:
            channel = grpc.insecure_channel(self.target, options=options)
        else:
            credentials = grpc.ssl_channel_credentials(root_certificates=custom_root_cert)
            channel = grpc.secure_channel(self.target, credentials, options=options)
        self.query = query_serv.QueryStub(channel)
        self.ingestion = ingest_serv.IngestStub(channel)
        self.seismicstub = seismic_serv.SeismicAPIStub(channel)

        if not no_retries:
            decorate_with_retries(self.query, self.ingestion, self.seismicstub)
        decorate_with_wrapped_rpc_errors(self.query, self.ingestion, self.seismicstub)

        self.survey = SurveyAPI(self.query, self.ingestion, self.metadata)
        self.file = FileAPI(self.query, self.ingestion, self.metadata)
        self.trace = TraceAPI(self.query, self.metadata)
        self.slice = SliceAPI(self.query, self.metadata)
        self.slab = SlabAPI(self.query, self.file, self.metadata)
        self.volume = VolumeAPI(self.query, self.ingestion, self.metadata)
        self.time_slice = TimeSliceAPI(self.query, self.metadata)
        self.job = JobAPI(self.ingestion, self.metadata)
        self.survey_v1 = SurveyV1API(self.seismicstub, self.metadata, self.survey)
        self.volume_seismic = VolumeSeismicAPI(self.seismicstub, self.ingestion, self.metadata)
        self.partition = PartitionAPI(self.seismicstub, self.ingestion, self.metadata)
        # The duplicated seismic/seismics is for making the rename backwards compatible.
        # The singular form is the one that we expect to keep after a breaking release.
        self.seismic = SeismicAPI(self.seismicstub, self.ingestion, self.metadata)
        self.seismics = SeismicAPI(self.seismicstub, self.ingestion, self.metadata)
        self.seismicstore = SeismicStoreAPI(self.seismicstub, self.ingestion, self.metadata)
        self.seismicstores = SeismicStoreAPI(self.seismicstub, self.ingestion, self.metadata)
        self.file_seismic = FileSeismicAPI(self.seismicstub, self.ingestion, self.metadata, self)
