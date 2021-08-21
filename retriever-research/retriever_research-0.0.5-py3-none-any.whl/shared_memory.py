# Threadsafe shared memory. Use this rarely - communication is typically better.
# The pykka actor registry won't let you set the URN by hand, instead always
# generating a uuid4. We add our own custom registry here to allow reference
# by predefined URN
import dataclasses
import datetime
import threading
from typing import Dict, Optional

import pykka
from retriever_research import messages
from retriever_research.config import Config, LogLevels
import pathlib

class RetrieverRegistryError(Exception):
    pass

@dataclasses.dataclass(frozen=True)
class FileDetail:
    file_id: str
    s3_bucket: str
    s3_key: str
    file_size: int

@dataclasses.dataclass(frozen=True)
class RetrieverRunMetadata:
    s3_region: str
    s3_prefix: str

class SharedMemory:
    def __init__(self, log_actor_ref: pykka.ActorRef):
        self._wip_lock = threading.Lock()
        self._wip = 0

        self.total_file_count = None

        self.log_actor_ref = log_actor_ref
        self.logging = Logger(log_actor_ref=self.log_actor_ref)

        self._file_details_lock = threading.Lock()
        self._file_details = {}  # type: Dict[str, FileDetail]

        self.metadata = None  # type: Optional[RetrieverRunMetadata]
        self.download_loc = None  # type: Optional[pathlib.Path]

    def increment_wip(self):
        with self._wip_lock:
            self._wip += 1

    def decrement_wip(self):
        with self._wip_lock:
            self._wip -= 1

    def get_wip(self):
        with self._wip_lock:  # Could get by without a lock I think
            return self._wip

    def add_file_details(self, file_id, s3_bucket, s3_key, file_size):
        with self._file_details_lock:
            self._file_details[file_id] = FileDetail(file_id=file_id, s3_bucket=s3_bucket, s3_key=s3_key, file_size=file_size)

    def get_file_details(self, file_id):
        with self._file_details_lock:
            return self._file_details[file_id]  # type: FileDetail


class Logger:
    def __init__(self, log_actor_ref: pykka.ActorRef):
        self.log_actor_ref = log_actor_ref

    def log(self, actor_urn: str, detail: str, level: LogLevels, log_id=None):
        log_msg = messages.LogMessage(
            actor=actor_urn,
            log=detail,
            log_id=log_id,
            level=level,
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
        )
        self.log_actor_ref.tell(log_msg)


