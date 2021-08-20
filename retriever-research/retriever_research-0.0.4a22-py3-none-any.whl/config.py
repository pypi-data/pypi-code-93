from enum import Enum

class Config:
    GIGA = 1_000_000_000
    MEGA = 1_000_000
    ACTOR_QUEUE_GET_TIMEOUT = 0.1
    TOO_MUCH_WIP_SLEEP_TIME = 0.1
    CHUNK_SIZE_BYTES = 8_000_000
    MAX_WIP = 40

    FILE_LIST_GENERATOR_URN = "FileListGenerator"
    FILE_CHUNKER_URN = "FileChunker"
    PARALLEL_CHUNK_DOWNLOADER_URN = "ParallelChunkDownloader"
    CHUNK_SEQUENCER_URN = "ChunkSequencer"
    FILE_WRITER_URN = "FileWriter"
    LOGGING_ACTOR_URN = "LoggingActor"
    ACTOR_WATCHER_URN = "ActorWatcher"


class LogLevels(str, Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO_VERBOSE = "INFO_VERBOSE"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


