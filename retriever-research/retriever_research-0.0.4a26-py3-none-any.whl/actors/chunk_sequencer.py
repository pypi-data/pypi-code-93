import queue
from typing import cast, Dict
import pykka

from retriever_research import messages
from retriever_research.shared_memory import SharedMemory
from retriever_research.config import Config
from retriever_research.actors import RetrieverThreadingActor

class PerFileState:
    def __init__(self, total_chunks_in_file):
        self.total_chunks = total_chunks_in_file
        self.current_seq_id = 0
        self.out_of_order_waiting_room = {}


class ChunkSequencer(RetrieverThreadingActor):
    use_daemon_thread = True

    def __init__(self, mem: SharedMemory, output_queue: queue.Queue):
        super().__init__(urn=Config.CHUNK_SEQUENCER_URN)
        self.output_queue = output_queue
        self.mem = mem

        self.per_file_state = {}  # type: Dict[str, PerFileState]
        self.num_files_done = 0
        self.total_files = None

    def on_receive(self, msg):
        assert type(msg) == messages.DownloadedChunkMsg
        msg = cast(messages.DownloadedChunkMsg, msg)
        if msg.file_id not in self.per_file_state:
            self.per_file_state[msg.file_id] = PerFileState(msg.total_chunks)

        file_state = self.per_file_state[msg.file_id]
        file_state.out_of_order_waiting_room[msg.seq_id] = msg

        while file_state.current_seq_id in file_state.out_of_order_waiting_room:
            next_result = file_state.out_of_order_waiting_room.pop(file_state.current_seq_id)
            self.output_queue.put(next_result)
            file_state.current_seq_id += 1

        if file_state.current_seq_id == file_state.total_chunks:
            self.num_files_done += 1
            if self.total_files is None:
                self.total_files = self.mem.total_file_count

            if self.total_files is not None:
                # TODO: Technically this could complete before the num_tracker gets set, leading to
                #  a hang, but that seems unlikely.
                if self.num_files_done == self.total_files:
                    self.output_queue.put(messages.DoneMsg())

    def on_stop(self) -> None:
        pass
        # print("ChunkSequencer onstop")
