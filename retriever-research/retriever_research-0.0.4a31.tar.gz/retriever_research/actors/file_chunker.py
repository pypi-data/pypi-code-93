import math
from typing import cast, Type
from types import TracebackType
import pykka

from retriever_research import messages
from retriever_research.config import Config, LogIds
from retriever_research.shared_memory import SharedMemory
from retriever_research.actors import RetrieverThreadingActor


class FileChunker(RetrieverThreadingActor):
    use_daemon_thread = True

    def __init__(self, mem: SharedMemory):
        super().__init__(urn=Config.FILE_CHUNKER_URN)
        self.mem = mem

        # Can't set ref in init as other actors may not have been created yet
        self.parallel_chunk_downloader_ref = None

    def on_start(self) -> None:
        self.parallel_chunk_downloader_ref = pykka.ActorRegistry.get_by_urn(Config.PARALLEL_CHUNK_DOWNLOADER_URN)
        assert self.parallel_chunk_downloader_ref is not None, "The ref should have been set"

    def on_receive(self, msg):
        assert type(msg) == messages.FileDownloadRequestMsg
        self.trace(f"received {msg}", log_id=LogIds.FILE_CHUNKER_RECEIVED_MESSAGE)

        msg = cast(messages.FileDownloadRequestMsg, msg)
        current_starting_byte = 0
        current_seq_id = 0
        total_chunks = math.ceil(msg.file_size / Config.CHUNK_SIZE_BYTES)

        while current_starting_byte <= msg.file_size:
            last_byte = min(current_starting_byte + Config.CHUNK_SIZE_BYTES - 1, msg.file_size)
            chunk_download_req = messages.ChunkDownloadRequestMsg(
                file_id=msg.file_id,
                s3_bucket=msg.s3_bucket,
                s3_key=msg.s3_key,
                s3_region=msg.s3_region,
                seq_id=current_seq_id,
                total_chunks=total_chunks,
                file_size=msg.file_size,
                first_byte=current_starting_byte,
                last_byte=last_byte
            )
            self.parallel_chunk_downloader_ref.tell(chunk_download_req)
            self.trace(f"sent {chunk_download_req}", log_id=LogIds.FILE_CHUNKER_SENT_MESSAGE)

            self.mem.increment_wip()
            current_starting_byte += Config.CHUNK_SIZE_BYTES
            current_seq_id += 1
