import pathlib
import typing

import pykka
import queue
import pathlib


from retriever_research.actors import ParallelChunkDownloader, FileChunker, FileListGenerator, FileWriter
from retriever_research.logging import LoggingActor
from retriever_research.actor_watcher import ObservabilityTicker, ActorWatcher
from retriever_research.config import Config, LogLevels, LogIds
from retriever_research import messages
from retriever_research.shared_memory import SharedMemory, RetrieverRunMetadata


class Retriever:
    def __init__(self):
        self.active = False
        self.shutdown_triggered = False
        self.output_queue = queue.Queue()

        # Create the log actor first so we can log
        self.log_actor_ref = LoggingActor.start(output_file="retriever.log")
        self.mem = SharedMemory(log_actor_ref=self.log_actor_ref)
        # self.mem.register_actor(Config.OBSERVABILITY_URN, self.observability_actor_ref)

        # Start all the other actors in multiple steps. Create actor, register into our custom registry,
        # then start the actor loop.
        # NOTE: __init__() executes during create().
        # NOTE: on_start() executes at the beginning of the actor loop.
        file_list_generator = FileListGenerator.create(mem=self.mem)
        file_chunker = FileChunker.create(mem=self.mem)
        parallel_chunk_downloader = ParallelChunkDownloader.create(mem=self.mem)
        file_writer = FileWriter.create(mem=self.mem, done_queue=self.output_queue)

        file_list_generator.start_actor_loop()
        file_chunker.start_actor_loop()
        parallel_chunk_downloader.start_actor_loop()
        file_writer.start_actor_loop()

        # Start monitoring infrastructure.
        self.obs_ticker = ObservabilityTicker(mem=self.mem, interval=1)
        self.actor_watcher_ref = ActorWatcher.start(mem=self.mem)

    def error(self, detail, log_id=None):
        self.log(detail, level=LogLevels.ERROR, log_id=log_id)

    def info(self, detail, log_id=None):
        self.log(detail, level=LogLevels.INFO, log_id=log_id)

    def info_verbose(self, detail, log_id=None):
        self.log(detail, level=LogLevels.INFO_VERBOSE, log_id=log_id)

    def trace(self, detail, log_id=None):
        self.log(detail, level=LogLevels.TRACE, log_id=log_id)

    def log(self, detail: str, level: LogLevels, log_id=None):
        self.mem.logging.log("Retriever", detail, level, log_id=log_id)

    def shutdown(self):
        self.info_verbose("shutdown triggered")
        self.shutdown_triggered = True

        # The observability infrastructure need to be shut down first because it watches the other actors
        self.trace("shutting down observability infrastructure (other than logging)", log_id=LogIds.RETRIEVER_SHUTDOWN)
        self.obs_ticker.stop()
        self.actor_watcher_ref.stop(block=True)
        self.obs_ticker.join()

        self.trace("signaling FileListGenerator to exit early in case it is still generating", log_id=LogIds.RETRIEVER_SHUTDOWN)
        # Tell File List Generator to shut down by
        flg_actor = pykka.ActorRegistry.get_by_urn(Config.FILE_LIST_GENERATOR_URN)._actor
        flg_actor = typing.cast(FileListGenerator, flg_actor)
        flg_actor.should_exit_early.set()

        # Trigger shutdown
        self.trace("shutting down main pipeline actors", log_id=LogIds.RETRIEVER_SHUTDOWN)
        # TODO: Parallelize shutdown (requires capturing errors during tell() caused by the actor no longer existing)
        for actor_urn in [Config.FILE_LIST_GENERATOR_URN,
                          Config.FILE_CHUNKER_URN,
                          Config.PARALLEL_CHUNK_DOWNLOADER_URN,
                          Config.FILE_WRITER_URN]:
            self.trace(f"shutting down {actor_urn}", log_id=LogIds.RETRIEVER_SHUTDOWN)
            pykka.ActorRegistry.get_by_urn(actor_urn).stop(block=True)
            self.trace(f"shut down {actor_urn}", log_id=LogIds.RETRIEVER_SHUTDOWN)


        # LoggingActor goes at the end so logging is available during shutdown
        self.trace("shutting down LoggingActor", log_id=LogIds.RETRIEVER_SHUTDOWN)
        pykka.ActorRegistry.get_by_urn(Config.LOGGING_ACTOR_URN).stop(block=True)


    def launch(self, s3_bucket, s3_prefix, s3_region, download_loc):
        self.info("Starting download")
        self.info_verbose(f"launch requested {s3_bucket} {s3_prefix} {s3_region}")
        self.active = True
        self.mem.metadata = RetrieverRunMetadata(s3_region=s3_region, s3_prefix=s3_prefix)
        self.mem.download_loc = pathlib.Path(download_loc)
        launch_msg = messages.RetrieveRequestMsg(s3_bucket=s3_bucket,
                                                 s3_prefix=s3_prefix,
                                                 s3_region=s3_region)
        pykka.ActorRegistry.get_by_urn(Config.FILE_LIST_GENERATOR_URN).tell(launch_msg)
        self.obs_ticker.start()

    # TODO: Rewrite this
    def _get_output(self):
        assert self.active, "Cannot call get_output before launching the pipeline"

        while True:
            if self.shutdown_triggered:
                return
            try:
                msg = self.output_queue.get(block=Config.ACTOR_QUEUE_GET_TIMEOUT)
            except queue.Empty:
                continue

            if isinstance(msg, messages.DoneMsg):
                self.log_actor_ref.tell(messages.CloseProgressBar())
                self.info("Download complete")
                break

    def get_output(self):
        try:
            self._get_output()
        except KeyboardInterrupt:
            print()
            self.log_actor_ref.tell(messages.CloseProgressBar())
            self.error("KeyboardInterrupt, shutting down")
        except Exception as e:
            self.log_actor_ref.tell(messages.CloseProgressBar())
            self.error(f"Received exception {type(e)}, shutting down ({e})")
        finally:
            self.log_actor_ref.tell(messages.CloseProgressBar())
            self.shutdown()