# Tooling to see what is happening while Retriever is running. Must be able to globally
# disable observability to measure performance impact. We need to minimize spam, but allow
# us to dig deeper into what is happening to investigate issues.

# The observability actor should store all data, but only expose a subset of it by default.


"""
What do we want to see?

- What actions are being taken by each actor
- See the path of messages through the system
"""

import json
from typing import Type
from types import TracebackType
import pykka

from retriever_research.shared_memory import SharedMemory
from retriever_research import messages
from retriever_research.ticker import Ticker
from retriever_research.config import Config, LogLevels
from retriever_research.actors.pykka_extensions.custom_actor import RetrieverThreadingActor

def print_log_line(log: messages.LogMessage):
    print(f'{log.timestamp.strftime("%H:%M:%S.%f")} - [{log.actor}] {log.log}')

class LoggingActor(RetrieverThreadingActor):
    # This actor must not reference any other actors. It is created before any others.
    can_log = False

    def __init__(self, output_file="retriever.log"):
        super().__init__(urn=Config.LOGGING_ACTOR_URN)
        self.output_file = output_file
        self.log_fileobj = open(self.output_file, "w")
        self.ignore_actor_list = []

    def on_receive(self, msg):
        assert isinstance(msg, messages.LogMessage)

        if isinstance(msg, messages.LogMessage):
            structured_log = dict(
                level=msg.level,
                log=msg.log,
                actor=msg.actor,
                timestamp=msg.timestamp.isoformat(),
            )
            if msg.log_id:
                structured_log["log_id"] = msg.log_id
            if msg.tags and len(msg.tags) > 0:
                structured_log["tags"] = msg.tags
            log_line = json.dumps(structured_log)
            self.log_fileobj.write(f"{log_line}\n")
            self.log_fileobj.flush()
            if structured_log["level"] in [LogLevels.INFO, LogLevels.ERROR]:
                print_log_line(msg)

    def on_start(self) -> None:
        pass
        # print("Observability on stop")

    def on_failure(
        self,
        exception_type: Type[BaseException],
        exception_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        pass
        # print(f"Observability on failure, {exception_type}, {exception_value}")








