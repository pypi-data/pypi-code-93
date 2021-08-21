import datetime
import logging
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
from retriever_research.config import Config, LogIds
from retriever_research.shared_memory import SharedMemory
from retriever_research.actors import RetrieverThreadingActor


def now_str():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S.%f")

def write_log_line(f, line):
    f.write(f"{now_str()} - {line}\n")
    f.flush()

def _work_loop(
        worker_id: int,
        task_queue: mp.Queue,
        result_queue: mp.Queue,
        shutdown_queue: mp.Queue,
):
    threading.current_thread().name = f"ParallelChunkDownloader-worker-{worker_id}"
    with open(f"worker_logs/worker_logs_{worker_id}.log", "w") as f:
        try:
            write_log_line(f, f"worker {worker_id} starting")
            boto3.set_stream_logger("", level=logging.ERROR)
            sess = boto3.session.Session()
            write_log_line(f, f"created boto3 session")
            s3_client = sess.client('s3')
            write_log_line(f, f"created s3_client")
            while True:
                try:
                    task = task_queue.get(timeout=Config.ACTOR_QUEUE_GET_TIMEOUT)
                    assert type(task) == messages.ChunkDownloadRequestMsg
                    write_log_line(f, f"received ChunkDownloadRequest to handle {task}")
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
                    write_log_line(f, f"finished downloading chunk")

                    continue
                except queue.Empty:
                    write_log_line(f, f'no ChunkDownloadRequest in queue, checking shutdown queue')
                    try:
                        shutdown_queue.get(block=False)
                        write_log_line(f, f"ParallelChunkDownloader._work_loop received ShutdownMessage, shutting down")
                        return
                    except queue.Empty:
                        write_log_line(f, f"No shutdown message, checking for new ChunkDownloadRequests")
                        continue
                except KeyboardInterrupt:
                    write_log_line(f, f"ParallelChunkDownloader._work_loop received KeyboardInterrupt, shutting down")
                    return
                except Exception as e:
                    write_log_line(f, f"ParallelChunkDownloader._work_loop got Exception, shutting down. {e}")
                    return
        except Exception as e:
            write_log_line(f, f"encountered unexpected exception {e}")


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

        if os.path.isdir("worker_logs"):
            self.trace("worker_logs directory already exists, deleting")
            shutil.rmtree('worker_logs')
        self.trace("creating worker_logs directory")
        os.mkdir("worker_logs")

        self.workers = [
            mp.Process(
                target=_work_loop,
                args=(i, self.task_queue, self.result_queue, self.shutdown_queues[i])
            )
            for i in range(num_workers)]
        self.trace(f"created {len(self.workers)} worker processes (not yet started)")

        # Thread that takes worker results and sends them on to the next actor
        self._output_forwarder_stop_signal = threading.Event()

        # Create a thread that forwards results from the worker result_queue to individual actors
        def _forward_results():
            while not self._output_forwarder_stop_signal.is_set():
                try:
                    result = self.result_queue.get(timeout=Config.ACTOR_QUEUE_GET_TIMEOUT)  # type: messages.DownloadedChunkMsg
                    if self.file_writer_ref is None:
                        self.file_writer_ref = pykka.ActorRegistry.get_by_urn(Config.FILE_WRITER_URN)
                    self.file_writer_ref.tell(result)
                    self.mem.decrement_wip()
                except queue.Empty:
                    pass
            self.trace("output forwarder thread shutting down")

        self._output_forwarder = threading.Thread(target=_forward_results)
        self._output_forwarder.name = "ParallelChunkDownloaderOutputForwarder"

    def on_start(self) -> None:
        self.file_writer_ref = pykka.ActorRegistry.get_by_urn(Config.FILE_WRITER_URN)
        assert self.file_writer_ref is not None

        self._output_forwarder.start()
        self.trace("output forwarder started")
        try:
            for worker in self.workers:
                worker.start()
        except Exception as e:
            raise e
        self.trace("started all worker processes")

    def on_receive(self, msg):
        assert type(msg) == messages.ChunkDownloadRequestMsg
        msg = cast(messages.ChunkDownloadRequestMsg, msg)
        self.trace(f"received {msg}", log_id=LogIds.PARALLEL_CHUNK_DOWNLOADER_RECEIVED_MESSAGE)
        self.task_queue.put(msg)

    def clean_shutdown(self) -> None:
        self.trace("signaling worker shutdown via shutdown queues")
        for i in range(self.num_workers):
            self.shutdown_queues[i].put(True)
        for i, worker in enumerate(self.workers):
            self.trace(f"terminating worker {i + 1} of {len(self.workers)}")
            worker.terminate()
            self.trace(f"waiting for worker {i + 1} of {len(self.workers)} to finish")
            worker.join()

        # Empty out all of the queues to prevent hanging
        self.trace("emptying task queue that prevents shutdown")
        while True:
            try:
                self.task_queue.get(block=False)
            except queue.Empty:
                break

        self.trace("emptying result queue that prevents shutdown")
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

