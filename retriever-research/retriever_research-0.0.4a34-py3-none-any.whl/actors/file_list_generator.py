import threading

import boto3
import time
import pykka

from retriever_research import messages
from retriever_research.config import Config, LogLevels, LogIds
from retriever_research.shared_memory import SharedMemory
from retriever_research.actors import RetrieverThreadingActor

class FileListGenerator(RetrieverThreadingActor):

    def __init__(self, mem: SharedMemory):
        super().__init__(urn=Config.FILE_LIST_GENERATOR_URN)
        self.mem = mem

        # Allow the actor to shut down in the middle of processing a message (which may take a long time)
        self.should_exit_early = threading.Event()

        # Can't set ref in init as other actors may not have been created yet
        self.file_chunker_ref = None
        self.buffer = []

        # boto3.set_stream_logger("")  # debug logs
        self.trace(f"creating boto3 sess", log_id=LogIds.BOTO3_BUG_TRACING)
        self.sess = boto3.session.Session()
        self.trace(f"created boto3 sess", log_id=LogIds.BOTO3_BUG_TRACING)
        self.s3_client = self.sess.client('s3')
        self.trace(f"created s3_client", log_id=LogIds.BOTO3_BUG_TRACING)

    def on_start(self) -> None:
        self.file_chunker_ref = pykka.ActorRegistry.get_by_urn(Config.FILE_CHUNKER_URN)

    def on_receive(self, msg):
        try:
            assert type(msg) == messages.RetrieveRequestMsg
            self.trace(f"received {msg}", log_id=LogIds.FILE_LIST_GENERATOR_RECEIVED_MESSAGE)

            num_files = 0
            # Call S3 API to list objects within the prefix.
            paginator = self.s3_client.get_paginator('list_objects_v2')
            self.trace(f"got list_objects_v2 paginator", log_id=LogIds.BOTO3_BUG_TRACING)
            response_iterator = paginator.paginate(
                Bucket=msg.s3_bucket,
                Prefix=msg.s3_prefix,
            )
            self.trace(f"created paginator iterator", log_id=LogIds.BOTO3_BUG_TRACING)

            # TODO: Keep listing even if rate limiter is preventing us from sending DownloadRequest
            #       downstream. We want to know the total number of files ASAP.
            for i, resp in enumerate(response_iterator):
                self.trace(f"reading page {i+1} of list v2 responses")
                for file in resp["Contents"]:
                    if self.should_exit_early.is_set():
                        return

                    key = file["Key"]
                    # etag = file["ETag"]
                    size = file["Size"]



                    file_id = f"s3://{msg.s3_bucket}/{key}"
                    self.mem.add_file_details(file_id=file_id, s3_bucket=msg.s3_bucket, s3_key=key, file_size=size)
                    self.buffer.append(messages.FileDownloadRequestMsg(
                        file_id=file_id,
                        s3_bucket=msg.s3_bucket,
                        s3_key=key,
                        s3_region=msg.s3_region,
                        file_size=size
                    ))
                    num_files += 1

                # If we can send more download requests downstream, send them
                while self.mem.get_wip() < Config.MAX_WIP:
                    if len(self.buffer) == 0:
                        break
                    msg = self.buffer.pop()  # type: messages.FileDownloadRequestMsg
                    self.file_chunker_ref.tell(msg)
                    self.info_verbose(f"Requested download of {msg.file_id}")

            self.info_verbose(f"Setting total file count to {num_files}")
            self.mem.total_file_count = num_files

            # Logger can't access SharedMemory
            self.mem.logging.log_actor_ref.tell(messages.ProgressInitMessage(num_files))

            if num_files == 0:
                raise RuntimeError("No files match prefix")

            # Send any messages still in the buffer downstream, rate-limited via a maximum amount of WIP
            # Note: WIP is measured in chunks, not files
            while True:
                if self.should_exit_early.is_set():
                    return

                if self.mem.get_wip() >= Config.MAX_WIP:
                    time.sleep(Config.TOO_MUCH_WIP_SLEEP_TIME)
                else:
                    if len(self.buffer) == 0:
                        self.trace("all FileDownloadRequests sent downstream")
                        return

                    msg = self.buffer.pop()  # type: messages.FileDownloadRequestMsg
                    self.file_chunker_ref.tell(msg)
                    self.info_verbose(f"Requested download of {msg.file_id}")


        except Exception as e:
            self.error(f"error during on_receive {e}", LogLevels.ERROR)

