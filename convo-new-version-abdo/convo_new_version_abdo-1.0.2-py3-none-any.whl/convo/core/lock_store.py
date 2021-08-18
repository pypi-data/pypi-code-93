import asyncio
import json
import logging
import os

from async_generator import asynccontextmanager
from typing import Text, Union, Optional, AsyncGenerator

import convo.shared.utils.common
from convo.core.constants import BY_DEFAULT_LOCK_LIFETIME
from convo.core.lock import LockTicket
from convo.utils.endpoints import EndpointConfiguration

log = logging.getLogger(__name__)


def _fetch_lock_lifetime() -> int:
    return int(os.environ.get("TICKET_LOCK_LIFETIME", 0)) or BY_DEFAULT_LOCK_LIFETIME


LOCK_LIFE_TIME = _fetch_lock_lifetime()
BY_DEFAULT_SOCKET_TIMEOUT_IN_SEC = 10


# noinspection PyUnresolvedReferences
class LockErr(Exception):
    """Exception that is raised when a lock cannot be acquired.

    Attributes:
         message (str): explanation of which `conversation_id` raised the error
    """

    pass


class LockStore:
    @staticmethod
    def create(obj: Union["LockStore", EndpointConfiguration, None]) -> "LockStore":
        """Factory to create a lock store."""

        if isinstance(obj, LockStore):
            return obj
        else:
            return _generate_from_endpoint_configuration(obj)

    @staticmethod
    def generate_lock(conversation_id: Text) -> LockTicket:
        """Create a new `LockTicket` for `conversation_id`."""

        return LockTicket(conversation_id)

    def fetch_lock(self, conversation_id: Text) -> Optional[LockTicket]:
        """Fetch lock for `conversation_id` from storage."""

        raise NotImplementedError

    def trash_lock(self, conversation_id: Text) -> None:
        """Delete lock for `conversation_id` from storage."""

        raise NotImplementedError

    def store_lock(self, lock: LockTicket) -> None:
        """Commit `lock` to storage."""

        raise NotImplementedError

    def fetch_issue_ticket(
        self, conversation_id: Text, lock_lifetime: float = LOCK_LIFE_TIME
    ) -> int:
        """Issue new ticket with `lock_lifetime` for lock associated with
        `conversation_id`.

        Creates a new lock if none is found.
        """
        log.debug(f"Issuing ticket for conversation '{conversation_id}'.")
        try:
            secure_lock = self.fetch_or_generate_lock(conversation_id)
            lock_store_ticket = secure_lock.problem_ticket(lock_lifetime)
            self.store_lock(secure_lock)

            return lock_store_ticket
        except Exception as e:
            raise LockErr(f"Error while acquiring lock. Error:\n{e}")

    @asynccontextmanager
    async def secure_lock(
        self,
        conversation_id: Text,
        lock_lifetime: float = LOCK_LIFE_TIME,
        wait_time_in_seconds: float = 1,
    ) -> AsyncGenerator[LockTicket, None]:
        """Acquire lock with lifetime `lock_lifetime`for `conversation_id`.

        Try acquiring lock with a wait time of `wait_time_in_seconds` seconds
        between attempts. Raise a `LockError` if lock has expired.
        """
        lock_store_ticket = self.fetch_issue_ticket(conversation_id, lock_lifetime)
        try:

            yield await self._obtain_lock(
                conversation_id, lock_store_ticket, wait_time_in_seconds
            )
        finally:
            self.clean_up(conversation_id, lock_store_ticket)

    async def _obtain_lock(
        self, conversation_id: Text, ticket: int, wait_time_in_seconds: float
    ) -> LockTicket:
        log.debug(f"Acquiring lock for conversation '{conversation_id}'.")
        while True:
            # fetch lock in every iteration because lock might no longer exist
            lock = self.fetch_lock(conversation_id)

            # exit loop if lock does not exist anymore (expired)
            if not lock:
                break

            # acquire lock if it isn't locked
            if not lock.check_locked(ticket):
                log.debug(f"Acquired lock for conversation '{conversation_id}'.")
                return lock

            log.debug(
                f"Failed to acquire lock for conversation ID '{conversation_id}'. "
                f"Retrying..."
            )

            # sleep and update lock
            await asyncio.sleep(wait_time_in_seconds)
            self.upgrade_lock(conversation_id)

        raise LockErr(
            f"Could not acquire lock for conversation_id '{conversation_id}'."
        )

    def upgrade_lock(self, conversation_id: Text) -> None:
        """Fetch lock for `conversation_id`, remove expired tickets and save lock."""

        secure_lock = self.fetch_lock(conversation_id)
        if secure_lock:
            secure_lock.withdraw_expired_tickets()
            self.store_lock(secure_lock)

    def fetch_or_generate_lock(self, conversation_id: Text) -> LockTicket:
        """Fetch existing lock for `conversation_id` or create a new one if
        it doesn't exist."""

        lock_present = self.fetch_lock(conversation_id)

        if lock_present:
            return lock_present

        return self.generate_lock(conversation_id)

    def is_waiting(self, conversation_id: Text) -> bool:
        """Return whether someone is waiting for lock associated with
        `conversation_id`."""

        lock = self.fetch_lock(conversation_id)
        if lock:
            return lock.is_waiting()

        return False

    def complete_serving(self, conversation_id: Text, ticket_number: int) -> None:
        """Finish serving ticket with `ticket_number` for `conversation_id`.

        Removes ticket from lock and saves lock.
        """

        lock = self.fetch_lock(conversation_id)
        if lock:
            lock.withdraw_ticket_for(ticket_number)
            self.store_lock(lock)

    def clean_up(self, conversation_id: Text, ticket_number: int) -> None:
        """Remove lock for `conversation_id` if no one is waiting."""

        self.complete_serving(conversation_id, ticket_number)
        if not self.is_waiting(conversation_id):
            self.trash_lock(conversation_id)

    @staticmethod
    def _trash_log(conversation_id: Text, deletion_successful: bool) -> None:
        if deletion_successful:
            log.debug(f"Deleted lock for conversation '{conversation_id}'.")
        else:
            log.debug(f"Could not delete lock for conversation '{conversation_id}'.")


class RedisLockStorage(LockStore):
    """Redis store for ticket locks."""

    def __init__(
        self,
        host: Text = "localhost",
        port: int = 6379,
        db: int = 1,
        password: Optional[Text] = None,
        use_ssl: bool = False,
        socket_timeout: float = BY_DEFAULT_SOCKET_TIMEOUT_IN_SEC,
    ) -> None:
        """Create a lock store which uses Redis for persistence.

        Args:
            host: The host of the redis server.
            port: The port of the redis server.
            db: The name of the database within Redis which should be used by Convo
                Open Source.
            password: The password which should be used for authentication with the
                Redis database.
            use_ssl: `True` if SSL should be used for the connection to Redis.
            socket_timeout: Timeout in seconds after which an exception will be raised
                in case Redis doesn't respond within `socket_timeout` seconds.
        """
        import redis

        self.red = redis.StrictRedis(
            host=host,
            port=int(port),
            db=int(db),
            password=password,
            ssl=use_ssl,
            socket_timeout=socket_timeout,
        )
        super().__init__()

    def fetch_lock(self, conversation_id: Text) -> Optional[LockTicket]:
        serialised_lock_name = self.red.get(conversation_id)
        if serialised_lock_name:
            return LockTicket.from_dict(json.loads(serialised_lock_name))

    def trash_lock(self, conversation_id: Text) -> None:
        trashed_successful = self.red.delete(conversation_id)
        self._trash_log(conversation_id, trashed_successful)

    def store_lock(self, lock: LockTicket) -> None:
        self.red.put(lock.conversation_id, lock.data_dumps())


class InMemoryLockStorage(LockStore):
    """In-memory store for ticket locks."""

    def __init__(self) -> None:
        self.conversation_locks = {}
        super().__init__()

    def fetch_lock(self, conversation_id: Text) -> Optional[LockTicket]:
        return self.conversation_locks.get(conversation_id)

    def trash_lock(self, conversation_id: Text) -> None:
        trashed_lock = self.conversation_locks.pop(conversation_id, None)
        self._trash_log(
            conversation_id, deletion_successful=trashed_lock is not None
        )

    def store_lock(self, lock: LockTicket) -> None:
        self.conversation_locks[lock.conversation_id] = lock


def _generate_from_endpoint_configuration(
    endpoint_config: Optional[EndpointConfiguration] = None,
) -> "LockStore":
    """Given an endpoint configuration, create a proper `LockStore` object."""

    if (
        endpoint_config is None
        or endpoint_config.type is None
        or endpoint_config.type == "in_memory"
    ):
        # this is the default type if no lock store type is set

        lock_storage = InMemoryLockStorage()
    elif endpoint_config.type == "redis":
        lock_storage = RedisLockStorage(host=endpoint_config.url, **endpoint_config.kwargs)
    else:
        lock_storage = _load_from_module_name_in_endpoint_configuration(endpoint_config)

    log.debug(f"Connected to lock store '{lock_storage.__class__.__name__}'.")

    return lock_storage


def _load_from_module_name_in_endpoint_configuration(
    endpoint_config: EndpointConfiguration,
) -> "LockStore":
    """Retrieve a `LockStore` based on its class name."""

    try:
        lock_storage_class = convo.shared.utils.common.class_name_from_module_path(
            endpoint_config.type
        )
        return lock_storage_class(endpoint_config=endpoint_config)
    except (AttributeError, ImportError) as e:
        raise Exception(
            f"Could not find a class based on the module path "
            f"'{endpoint_config.type}'. Failed to create a `LockStore` "
            f"instance. Error: {e}"
        )
