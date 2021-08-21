import datetime
from typing import Dict, List, Optional
import dataclasses
from retriever_research.config import LogLevels

@dataclasses.dataclass
class SetNumFiles:
    num_files: int

class QueryNumFiles:
    pass

class QueryWIP:
    pass

class IncrementWIP:
    pass

class DecrementWIP:
    pass

@dataclasses.dataclass
class RetrieveRequestMsg:
    s3_bucket: str
    s3_prefix: str
    s3_region: str


@dataclasses.dataclass
class PassthroughMsg:
    msg_id: str
    custom: Dict = dataclasses.field(default_factory=lambda: {})


@dataclasses.dataclass
class FileDownloadRequestMsg:
    file_id: str
    s3_bucket: str
    s3_key: str
    s3_region: str
    file_size: int  # in bytes


@dataclasses.dataclass
class ChunkDownloadRequestMsg:
    file_id: str
    s3_bucket: str
    s3_key: str
    s3_region: str
    file_size: int  # in bytes
    seq_id: int
    total_chunks: int
    first_byte: int  # inclusive
    last_byte: int  # inclusive


@dataclasses.dataclass
class DownloadedChunkMsg:
    file_id: str
    seq_id: int
    total_chunks: int
    content: bytes

    def __repr__(self):
        return str(dict(
            file_id=self.file_id,
            seq_id=self.seq_id,
            total_chunks=self.total_chunks,
            content=f"({len(self.content)} bytes)"
        ))

class DoneMsg:
    pass



@dataclasses.dataclass
class LogMessage:
    log: str
    actor: str
    level: LogLevels
    timestamp: datetime.datetime
    log_id: Optional[str] = None
    tags: Optional[List[str]] = None

    @staticmethod
    def from_json(j: Dict):
        l = LogMessage(
            log=j["log"],
            actor=j["actor"],
            level=LogLevels[j["level"]],
            timestamp=datetime.datetime.fromisoformat(j["timestamp"])
        )
        if "log_id" in j.keys():
            l.log_id = j["log_id"]
        if "tags" in j.keys():
            l.tags = j["tags"]
        return l



class ProgressUpdateMessage:
    pass

@dataclasses.dataclass
class ProgressInitMessage:
    total_files: int

class CloseProgressBar:
    pass

@dataclasses.dataclass
class ObservabilityMessage:
    timestamp: datetime.datetime
    actor: str
    detail: str


class ObservabilityTick:
    pass