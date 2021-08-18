import json
import logging
from collections import deque

import time
from typing import Text, Optional, Union, Deque, Dict, Any

log = logging.getLogger(__name__)

NO_TICKET_PERMITTED = -1  # index of latest issued ticket if no tickets exist


class Lock_Ticket:
    def __init__(self, number: int, expires: float) -> None:
        self.number = number
        self.expires = expires

    def have_expired(self) -> bool:
        return time.time() > self.expires

    def as_dictionary(self) -> Dict[Text, Any]:
        return dict(number=self.number, expires=self.expires)

    def trash(self) -> Text:
        """Return json dump of `Lock_Ticket` as dictionary."""

        return json.dumps(self.as_dictionary())

    @classmethod
    def from_dict(cls, data: Dict[Text, Union[int, float]]) -> "Lock_Ticket":
        """Creates `Lock_Ticket` from dictionary."""

        return cls(number=data["number"], expires=data["expires"])

    def __repr__(self) -> Text:
        return f"Lock_Ticket(number: {self.number}, expires: {self.expires})"


class LockTicket:
    """Locking mechanism that issues tickets managing access to conversation IDs.

    Tickets are issued in the order in which they are requested. A detailed
    explanation of the ticket lock algorithm can be found at
    http://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks.pdf#page=13
    """

    def __init__(
        self, conversation_id: Text, tickets: Optional[Deque[Lock_Ticket]] = None
    ) -> None:
        self.conversation_id = conversation_id
        self.tickets = tickets or deque()

    @classmethod
    def from_dict(cls, data: Dict[Text, Any]) -> "LockTicket":
        """Create `LockTicket` from dictionary."""

        lock_tickets = [Lock_Ticket.from_dict(json.loads(d)) for d in data.get("tickets")]
        return cls(data.get("conversation_id"), deque(lock_tickets))

    def data_dumps(self) -> Text:
        """Return json dump of `LockTicket`."""

        tickets = [ticket.trash() for ticket in self.tickets]
        return json.dumps(dict(conversation_id=self.conversation_id, tickets=tickets))

    def check_locked(self, ticket_number: int) -> bool:
        """Return whether `ticket_number` is locked.

        Returns:
             True if `now_serving` is not equal to `ticket`.
        """

        return self.now_serv != ticket_number

    def problem_ticket(self, lifetime: float) -> int:
        """Issue a new ticket and return its number."""

        self.withdraw_expired_tickets()
        lock_no = self.previous_issued + 1
        lock_ticket = Lock_Ticket(lock_no, time.time() + lifetime)
        self.tickets.append(lock_ticket)

        return lock_no

    def withdraw_expired_tickets(self) -> None:
        """Remove expired tickets."""

        # iterate over copy of self.tickets so we can remove items
        for ticket in list(self.tickets):
            if ticket.have_expired():
                self.tickets.remove(ticket)

    @property
    def previous_issued(self) -> int:
        """Return number of the ticket that was last added.

        Returns:
             Number of `Lock_Ticket` that was last added. `NO_TICKET_ISSUED` if no
             tickets exist.
        """

        ticket_no = self._ticket_no_for(-1)

        return ticket_no if ticket_no is not None else NO_TICKET_PERMITTED

    @property
    def now_serv(self) -> Optional[int]:
        """Get number of the ticket to be served next.

        Returns:
             Number of `Lock_Ticket` that is served next. 0 if no `Lock_Ticket` exists.
        """

        return self._ticket_no_for(0) or 0

    def _ticket_no_for(self, ticket_index: int) -> Optional[int]:
        """Get ticket number for `ticket_index`.

        Returns:
             Lock_Ticket number for `Lock_Ticket` with index `ticket_index`. None if there are no
             tickets, or if `ticket_index` is out of bounds of `self.tickets`.
        """

        self.withdraw_expired_tickets()

        try:
            return self.tickets[ticket_index].number
        except IndexError:
            return None

    def _ticket_for_ticket_no(self, ticket_number: int) -> Optional[Lock_Ticket]:
        """Return ticket for `ticket_number`."""

        self.withdraw_expired_tickets()

        return next((t for t in self.tickets if t.number == ticket_number), None)

    def is_waiting(self) -> bool:
        """Return whether someone is waiting for the lock to become available.

        Returns:
             True if the `self.tickets` queue has length greater than 0.
        """

        return len(self.tickets) > 0

    def withdraw_ticket_for(self, ticket_number: int) -> None:
        """Remove `Lock_Ticket` for `ticket_number."""

        ticket = self._ticket_for_ticket_no(ticket_number)
        if ticket:
            self.tickets.remove(ticket)
