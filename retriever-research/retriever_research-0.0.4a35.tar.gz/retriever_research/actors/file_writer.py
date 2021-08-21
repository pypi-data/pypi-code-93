import queue
from typing import cast, Dict, Type
from types import TracebackType
import pykka
import os

from retriever_research import messages
from retriever_research.shared_memory import SharedMemory
from retriever_research.config import Config, LogIds
from retriever_research.actors import RetrieverThreadingActor

class FileState:
    def __init__(self, file_id, save_path, total_chunks_in_file):
        self.file_id = file_id
        self.total_chunks = total_chunks_in_file
        self.save_path = save_path
        self.current_seq_id = 0
        self.out_of_order_waiting_room = {}  # type: Dict[int, messages.DownloadedChunkMsg]
        self.fileobj = open(self.save_path, 'wb')

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever

class FileWriter(RetrieverThreadingActor):
    use_daemon_thread = True

    def __init__(self, mem: SharedMemory, done_queue: queue.Queue):
        super().__init__(urn=Config.FILE_WRITER_URN)
        self.done_queue = done_queue
        self.mem = mem

        self.per_file_state = {}  # type: Dict[str, FileState]
        self.num_files_done = 0
        self.total_files = None
        self.total_bytes_written = 0

    def on_receive(self, msg):
        try:
            assert type(msg) == messages.DownloadedChunkMsg
            msg = cast(messages.DownloadedChunkMsg, msg)
            self.trace(f"received {msg}", log_id=LogIds.FILE_WRITER_RECEIVED_MESSAGE)

            if msg.file_id not in self.per_file_state:
                req_prefix = self.mem.metadata.s3_prefix
                download_dir = self.mem.download_loc

                local_rel_path = None

                # TODO: Is this logic consistently correct?
                # If the requested s3 prefix is a single key, use the last portion of the s3_key to save it
                file_key = self.mem.get_file_details(msg.file_id).s3_key
                if req_prefix == file_key:
                    local_rel_path = req_prefix.split("/")[-1]
                else:
                    # If the request prefix ends with a slash or could end with a slash, consider that to
                    # be the directory. Otherwise find the parent directory.
                    """
                    Example:
                    s3://bucket/dir/key1
                    s3://bucket/dir/key2
                    
                    These should all have the same behavior in terms of output directory structure:
                    download s3://bucket/dir
                    download s3://bucket/dir/
                    download s3://bucket/dir/k
                    """
                    req_is_directory = req_prefix.endswith("/") or remove_prefix(file_key, req_prefix).startswith("/")
                    if req_is_directory:
                        local_rel_path = remove_prefix(file_key, req_prefix).lstrip("/")
                    else:
                        trailing_chars = len(req_prefix.split("/")[-1])
                        req_prefix_dir = req_prefix[:-trailing_chars]
                        local_rel_path = remove_prefix(file_key, req_prefix_dir).lstrip("/")

                download_path = download_dir / local_rel_path
                # print(f"Downloading new file to {download_path}")

                # Make any nested directories required
                os.makedirs(os.path.dirname(download_path), exist_ok=True)
                self.trace(f"have not seen {msg.file_id} before, creating new file {download_path}")
                self.per_file_state[msg.file_id] = FileState(msg.file_id, download_path, msg.total_chunks)

            file_state = self.per_file_state[msg.file_id]
            file_state.out_of_order_waiting_room[msg.seq_id] = msg

            # If we have any in-order chunks, write them out to the file
            while file_state.current_seq_id in file_state.out_of_order_waiting_room:
                next_result = file_state.out_of_order_waiting_room.pop(file_state.current_seq_id)  # type: messages.DownloadedChunkMsg
                file_state.fileobj.write(next_result.content)
                self.total_bytes_written += len(next_result.content)
                file_state.current_seq_id += 1

            # Finished downloading this file?
            if file_state.current_seq_id == file_state.total_chunks:

                file_state.fileobj.close()
                self.num_files_done += 1

                if self.total_files is None:
                    self.total_files = self.mem.total_file_count

                total = self.total_files if self.total_files else '?'
                self.trace(f"completed file {file_state.file_id} (#{self.num_files_done} completed of {total} total)")
                self.mem.log_actor_ref.tell(messages.ProgressUpdateMessage())

                del self.per_file_state[file_state.file_id]
                if self.total_files is not None:
                    # TODO: Technically this could complete before the num_tracker gets set, leading to
                    #  a hang, but that seems unlikely.
                    if self.num_files_done == self.total_files:
                        self.info_verbose(f"downloaded {self.total_bytes_written} bytes ({self.total_files} files)")
                        self.done_queue.put(messages.DoneMsg())
            self.trace(f"{len(self.per_file_state)} file downloads in progress", log_id=LogIds.FILE_WRITER_WIP_WATCHER)
        except Exception as e:
            print(f"failed during on_receive: {e}")
            self.error(f"failed during on_receive: {e}")
            raise e

    def on_stop(self) -> None:
        for file_id, file_state in self.per_file_state.items():
            file_state.fileobj.close()

    def on_failure(
        self,
        exception_type: Type[BaseException],
        exception_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        for file_id, file_state in self.per_file_state.items():
            file_state.fileobj.close()
