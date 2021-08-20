import pathlib
import typing

import pykka
import queue
import pathlib


from retriever_research.actors import ParallelChunkDownloader, FileChunker, FileListGenerator, FileWriter
from retriever_research.logging import LoggingActor
from retriever_research.actor_watcher import ObservabilityTicker, ActorWatcher
from retriever_research.config import Config
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

    def shutdown(self):
        self.shutdown_triggered = True

        # The observability infrastructure need to be shut down first because it watches the other actors
        self.obs_ticker.stop()
        self.actor_watcher_ref.stop(block=True)
        self.obs_ticker.join()

        # Tell File List Generator to shut down by
        flg_actor = pykka.ActorRegistry.get_by_urn(Config.FILE_LIST_GENERATOR_URN)._actor
        flg_actor = typing.cast(FileListGenerator, flg_actor)
        flg_actor.should_exit_early.set()

        # Trigger shutdown
        # TODO: Parallelize shutdown (requires capturing errors during tell() caused by the actor no longer existing)
        stops = []
        stops.append((Config.FILE_LIST_GENERATOR_URN, pykka.ActorRegistry.get_by_urn(Config.FILE_LIST_GENERATOR_URN).stop(block=True)))
        stops.append((Config.FILE_CHUNKER_URN, pykka.ActorRegistry.get_by_urn(Config.FILE_CHUNKER_URN).stop(block=True)))
        stops.append((Config.PARALLEL_CHUNK_DOWNLOADER_URN, pykka.ActorRegistry.get_by_urn(Config.PARALLEL_CHUNK_DOWNLOADER_URN).stop(block=True)))
        stops.append((Config.FILE_WRITER_URN, pykka.ActorRegistry.get_by_urn(Config.FILE_WRITER_URN).stop(block=True)))

        # LoggngActor goes at the end so logging is available during shutdown
        pykka.ActorRegistry.get_by_urn(Config.LOGGING_ACTOR_URN).stop(block=True)


    def launch(self, s3_bucket, s3_prefix, s3_region, download_loc):
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
            if isinstance(msg, messages.DownloadedChunkMsg):
                pass
                # if msg.seq_id % 10 == 0:
                #     print(f"Received chunk {msg.seq_id+1} of {msg.total_chunks}")
            elif isinstance(msg, messages.DoneMsg):
                print("Received all chunks!")
                break

    def get_output(self):
        try:
            self._get_output()
        except KeyboardInterrupt:
            print()
            print("KeyboardInterrupt: shutting down")
        except Exception as e:
            pass
        finally:
            self.shutdown()