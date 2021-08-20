import datetime
import os
import queue
import threading
from typing import cast, Type
from types import TracebackType
import multiprocessing as mp
import boto3
import shutil
import pykka

from retriever_research import messages
from retriever_research.config import Config
from retriever_research.shared_memory import SharedMemory
from retriever_research.actors import RetrieverThreadingActor


def now_str():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S.%f")

# TODO: Pass in an identifier for each process
def _work_loop(
        worker_id: int,
        task_queue: mp.Queue,
        result_queue: mp.Queue,
        shutdown_queue: mp.Queue,
):

    with open(f"worker_logs/worker_logs_{worker_id}.log", "w") as f:
        try:
            f.write(f"{now_str()} - worker {worker_id} starting\n")
            f.flush()
            s3_client = boto3.session.Session().client('s3')
            f.write(f"{now_str()} - created s3_client\n")
            f.flush()
            while True:
                try:
                    task = task_queue.get(timeout=Config.ACTOR_QUEUE_GET_TIMEOUT)
                    assert type(task) == messages.ChunkDownloadRequestMsg
                    f.write(f"{now_str()} - received ChunkDownloadRequest to handle {task}\n")
                    f.flush()
                    task = cast(messages.ChunkDownloadRequestMsg, task)

                    range_str = f"bytes={task.first_byte}-{task.last_byte}"
                    response = s3_client.get_object(Bucket=task.s3_bucket, Key=task.s3_key, Range=range_str)
                    content = response["Body"].read()
                    result = messages.DownloadedChunkMsg(
                        file_id=task.file_id,
                        seq_id=task.seq_id,
                        total_chunks=task.total_chunks,
                        content=content
                    )
                    result_queue.put(result)
                    f.write(f"{now_str()} - finished downloading chunk\n")
                    f.flush()

                    continue
                except queue.Empty:
                    f.write(f'{now_str()} - no ChunkDownloadRequest in queue, checking shutdown queue\n')
                    f.flush()
                    try:
                        shutdown_queue.get(block=False)
                        f.write(f"{now_str()} - ParallelChunkDownloader._work_loop received ShutdownMessage, shutting down\n")
                        f.flush()
                        return
                    except queue.Empty:
                        f.write(f"{now_str()} - No shutdown message, checking for new ChunkDownloadRequests\n")
                        continue
                except KeyboardInterrupt:
                    f.write(f"{now_str()} - ParallelChunkDownloader._work_loop received KeyboardInterrupt, shutting down\n")
                    f.flush()
                    return
                except Exception as e:
                    f.write(f"{now_str()} - ParallelChunkDownloader._work_loop got Exception, shutting down. {e}\n")
                    f.flush()
                    return
        except Exception as e:
            f.write(f"encountered unexpected exception {e}\n")
            f.flush()


class ParallelChunkDownloader(RetrieverThreadingActor):
    use_daemon_thread = True

    def __init__(self, mem: SharedMemory, num_workers=None):
        super().__init__(urn=Config.PARALLEL_CHUNK_DOWNLOADER_URN)
        self.mem = mem

        # Can't set ref in init as other actors may not have been created yet
        self.file_writer_ref = None

        if num_workers is None:
            num_workers = mp.cpu_count()

        self.num_workers = num_workers

        # Create workers and task queues
        self.task_queue = mp.Queue()
        self.result_queue = mp.Queue()
        self.shutdown_queues = [mp.Queue() for _ in range(self.num_workers)]

        # TODO: Fix client to use correct region.
        # Note: Instantiating an boto3 client is not multiprocessing safe.
        # self.boto_clients = [boto3.client('s3') for _ in range(self.num_workers)]

        if os.path.isdir("worker_logs"):
            shutil.rmtree('worker_logs')
        os.mkdir("worker_logs")


        self.workers = [
            mp.Process(
                target=_work_loop,
                # args=(self.task_queue, self.result_queue, self.shutdown_queues[i], self.boto_clients[i])
                args=(i, self.task_queue, self.result_queue, self.shutdown_queues[i])
            )
            for i in range(num_workers)]

        # Thread that takes worker results and sends them on to the next actor
        self._output_forwarder_stop_signal = threading.Event()

        def _forward_results():
            while not self._output_forwarder_stop_signal.is_set():
                try:
                    result = self.result_queue.get(timeout=Config.ACTOR_QUEUE_GET_TIMEOUT)  # type: messages.DownloadedChunkMsg
                    if self.file_writer_ref is None:
                        self.file_writer_ref = pykka.ActorRegistry.get_by_urn(Config.FILE_WRITER_URN)
                        self.log(self.file_writer_ref)
                    self.file_writer_ref.tell(result)
                    self.mem.decrement_wip()
                except queue.Empty:
                    pass

        self._output_forwarder = threading.Thread(target=_forward_results)
        self._output_forwarder.name = "ParallelChunkDownloaderOutputForwarder"

    def on_start(self) -> None:
        self.file_writer_ref = pykka.ActorRegistry.get_by_urn(Config.FILE_WRITER_URN)
        assert self.file_writer_ref is not None

        self._output_forwarder.start()
        try:
            for worker in self.workers:
                worker.start()
        except Exception as e:
            raise e
        # self.log("on_start completed")

    def on_receive(self, msg):
        assert type(msg) == messages.ChunkDownloadRequestMsg
        msg = cast(messages.ChunkDownloadRequestMsg, msg)
        self.task_queue.put(msg)

    def clean_shutdown(self) -> None:
        self.trace("signaling worker shutdown via shutdown queues")
        for i in range(self.num_workers):
            self.shutdown_queues[i].put(True)
        for i, worker in enumerate(self.workers):
            self.trace(f"waiting for worker {i + 1} of {len(self.workers)} to finish")
            worker.join()

        # Empty out all of the queues to prevent hanging
        self.trace("emptying task queues that prevent shutdown")
        while True:
            try:
                self.task_queue.get(block=False)
            except queue.Empty:
                break

        self.trace("emptying result queues that prevent shutdown")
        while True:
            try:
                self.result_queue.get(block=False)
            except queue.Empty:
                break

        self.trace("signaling output forward to stop")
        self._output_forwarder_stop_signal.set()
        self._output_forwarder.join()
        self.trace("output forwarder stopped")

    def on_stop(self) -> None:
        self.trace("on_stop, cleaning up")
        self.clean_shutdown()
        self.trace("on_stop complete")



    def on_failure(
        self,
        exception_type: Type[BaseException],
        exception_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        self.trace("on_failure, cleaning up")
        self.clean_shutdown()
        self.trace("on_failure complete")

