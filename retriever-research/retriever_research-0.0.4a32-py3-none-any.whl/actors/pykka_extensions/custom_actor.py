import threading
import uuid
import pykka
import sys
import logging
from typing import Type
from types import TracebackType
from pykka import messages as pykkamessages

from retriever_research.shared_memory import SharedMemory
from retriever_research.config import LogLevels, LogIds

# Change some details of Pykka's ThreadingActor to get additional features.
#   - Split actor start into two steps so that we can create all of the actors before running
#     on_start() for any actors (so they can reference each other)
#   - Allow a URN to be set manually
#   - Always use daemon_threads
#   - Automatically log some actor system actions and state
#   - Expose an easy-to-use log function
# Based on pykka 3.0.1


logger = logging.getLogger("pykka")

class RetrieverThreadingActor(pykka.ThreadingActor):
    use_daemon_thread = True
    can_log = True  # Set this to false if we want to disable logging. This is for the
                    # logging actor to use because it can't log itself shutting down

    def __init__(self, urn, *args, **kwargs):
        # Overwrite the logic we don't like in pykka.Actor. Change the actor urn so it can be
        # passed in at creation time.
        self.actor_urn = urn if urn is not None else uuid.uuid4().urn
        self.actor_inbox = self._create_actor_inbox()
        self.actor_stopped = threading.Event()
        self.actor_ref = pykka.ActorRef(self)

    @classmethod
    def create(cls, *args, **kwargs) -> "RetrieverThreadingActor":
        """
        Split object creation/registration from actor loop execution. Now we can create all
        the actors at once and then have them reference each other in on_start().

        No code changes (one log line removed). Just splitting up lines into create() and start_actor_loop().
        """
        obj = cls(*args, **kwargs)

        assert obj.actor_ref is not None, (
            "Actor.__init__() have not been called. "
            "Did you forget to call super() in your override?"
        )
        pykka.ActorRegistry.register(obj.actor_ref)
        return obj

    def start_actor_loop(self):
        self._start_actor_loop()
        return self.actor_ref

    ########################################################################
    # Add logging
    ########################################################################
    # Make logging available with high-level APIs. Only works for actors that store SharedMemory as self.mem
    # Sends log information to Observability actor
    def log(self, detail, level: LogLevels = LogLevels.INFO, log_id=None):
        if not self.can_log:
            return

        assert hasattr(self, 'mem'), "The log() function only works for actors that have shared memory " \
                                     "stored in self.mem. self.mem not set"
        assert isinstance(self.mem, SharedMemory), "The log() function only works for actors that have " \
                                                   "shared memory stored in self.mem. self.mem not of " \
                                                   "type SharedMemory"
        self.mem.logging.log(self.actor_urn, detail, level, log_id=log_id)

    def error(self, detail, log_id=None):
        self.log(detail, LogLevels.ERROR, log_id=log_id)

    def info_verbose(self, detail, log_id=None):
        self.log(detail, LogLevels.INFO_VERBOSE, log_id=log_id)

    def info(self, detail, log_id=None):
        self.log(detail, LogLevels.INFO, log_id=log_id)

    def debug(self, detail, log_id=None):
        self.log(detail, LogLevels.DEBUG, log_id=log_id)

    def trace(self, detail, log_id=None):
        self.log(detail, LogLevels.TRACE, log_id=log_id)


    ########################################################################
    # Change the actor loop to introduce new behavior to all Actors
    ########################################################################
    def _before_on_start(self):
        self.trace("on_start triggered", log_id=LogIds.ACTOR_SYSTEM_TRACES)

    def _before_on_stop(self):
        self.trace("on_stop triggered", log_id=LogIds.ACTOR_SYSTEM_TRACES)

    def _before_on_failure(
            self,
        exception_type: Type[BaseException],
        exception_value: BaseException,
        traceback: TracebackType
    ):
        self.trace(f"on_failure triggered. {exception_type}, {exception_value}", log_id=LogIds.ACTOR_SYSTEM_TRACES)

    def _actor_loop(self):
        """
        The actor's event loop.

        Modifications:
        Add hooks for logging:
        - _before_on_start()
        - _before_on_stop()
        - _before_on_failure()
        """

        ######## Changed
        try:
            self._before_on_start()
        except Exception:
            self._handle_failure(*sys.exc_info())
        ####### END CHANGED

        try:
            self.on_start()
        except Exception:
            self._handle_failure(*sys.exc_info())

        while not self.actor_stopped.is_set():
            envelope = self.actor_inbox.get()
            try:
                response = self._handle_receive(envelope.message)
                if envelope.reply_to is not None:
                    envelope.reply_to.set(response)
            except Exception:
                if envelope.reply_to is not None:
                    logger.info(
                        f"Exception returned from {self} to caller:",
                        exc_info=sys.exc_info(),
                    )
                    envelope.reply_to.set_exception()
                else:
                    self._handle_failure(*sys.exc_info())
                    ###### CHANGED
                    try:
                        self._before_on_failure(*sys.exc_info())
                    except Exception:
                        self._handle_failure(*sys.exc_info())
                    ###### END CHANGED
                    try:
                        self.on_failure(*sys.exc_info())
                    except Exception:
                        self._handle_failure(*sys.exc_info())
            except BaseException:
                exception_value = sys.exc_info()[1]
                logger.debug(f"{exception_value!r} in {self}. Stopping all actors.")
                self._stop()
                pykka.ActorRegistry.stop_all()

        while not self.actor_inbox.empty():
            envelope = self.actor_inbox.get()
            if envelope.reply_to is not None:
                if isinstance(envelope.message, pykkamessages._ActorStop):
                    envelope.reply_to.set(None)
                else:
                    envelope.reply_to.set_exception(
                        exc_info=(
                            pykka.ActorDeadError,
                            pykka.ActorDeadError(
                                f"{self.actor_ref} stopped before "
                                f"handling the message"
                            ),
                            None,
                        )
                    )

    def _stop(self):
        """
        Stops the actor immediately without processing the rest of the inbox.
        """
        pykka.ActorRegistry.unregister(self.actor_ref)
        self.actor_stopped.set()
        logger.debug(f"Stopped {self}")
        ###### CHANGED
        try:
            self._before_on_stop()
        except Exception as e:
            self._handle_failure(*sys.exc_info())
        ###### END CHANGED

        try:
            self.on_stop()
        except Exception:
            self._handle_failure(*sys.exc_info())


