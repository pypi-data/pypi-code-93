import json
from typing import Type
from types import TracebackType
import pykka

from retriever_research.shared_memory import SharedMemory
from retriever_research import messages
from retriever_research.ticker import Ticker
from retriever_research.config import Config, LogLevels, LogIds
from retriever_research.actors.pykka_extensions.custom_actor import RetrieverThreadingActor
from retriever_research import messages




class ActorWatcher(RetrieverThreadingActor):
    def __init__(self, mem: SharedMemory):
        super().__init__(urn=Config.ACTOR_WATCHER_URN)
        self.mem = mem

    def on_receive(self, msg: messages.ObservabilityTick):
        actors_to_monitor = [
            Config.FILE_LIST_GENERATOR_URN,
            Config.FILE_CHUNKER_URN,
            Config.PARALLEL_CHUNK_DOWNLOADER_URN,
            Config.FILE_WRITER_URN
        ]

        outs = []
        for actor_urn in actors_to_monitor:
            actor_ref = pykka.ActorRegistry.get_by_urn(actor_urn)
            # print(actor_urn)
            try:
                is_stopped = actor_ref.actor_stopped.is_set()
            except Exception as e:
                self.error(f"Exception when checking if actor stop for {actor_urn} is_set ({e})")
                # print(f"Error when checking if actor {actor_urn} has stopped")
                raise e
            display_str = "Stopped" if is_stopped else "Running"
            outs.append({actor_urn: display_str})

        self.log(str(outs), LogLevels.TRACE, log_id=LogIds.ACTOR_WATCHER_UPDATE)


class ObservabilityTicker(Ticker):
    def execute(self):
        actor_watcher_ref = pykka.ActorRegistry.get_by_urn(Config.ACTOR_WATCHER_URN)
        if actor_watcher_ref is None:
            self.mem.logging.log("ObservabilityTicker", "Unable to get ActorWatcherRef", LogLevels.WARN)
            return

        actor_watcher_ref.tell(messages.ObservabilityTick())