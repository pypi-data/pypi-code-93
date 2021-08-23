"""
    The Auction class represents an auction on a Board.
"""

from typing import Dict, List, Union

__all__ = ['Auction']

from .call import Call
from .constants import SEATS, CALLS


class Auction(object):
    """
    An Auction object for the bridgeobjects module.

    Usually the first_caller is the dealer.

    The attribute calls is a list of Call objects.
    The attribute note_keys is a list of keys to the notes dict.
    The two lists must have the same number of elements.

    Parameters
    ----------
    calls : (None or a list of calls or call names)
    first_caller : (str)
        First call for the auction (Generally implemented by a rich PBN file)
    """

    def __init__(self, calls: Union[List[Call], None]=None, first_caller: str=''):
        """Create an auction with the given calls and first_caller."""
        self.first_caller = first_caller
        if not calls:
            calls = []
        self._calls = []
        for call in calls:
            if isinstance(call, str):
                call = Call(call)
            self._calls.append(call)
        self._note_keys: List[str] = []
        self._notes: Dict[str, str] = {}

    def __repr__(self) -> str:
        """Return the repr string for the object."""
        return f'Auction: {self._get_call_names()}'

    def __str__(self) -> str:
        """Return the str string for the object."""
        return f'Auction: {self._get_call_names()}'

    def _get_call_names(self) -> str:
        """Return call names as a string."""
        call_names = [call.name for call in self._calls]
        return ', '.join(call_names)

    @property
    def first_caller(self) -> Union[str, None]:
        """Return the first_caller value."""
        return self._first_caller

    @first_caller.setter
    def first_caller(self, value):
        """Assign the first_caller value."""
        if value:
            if not isinstance(value, str):
                raise TypeError('First caller must be a string')
            if value not in SEATS:
                raise ValueError(f'{value} is not a valid seat')
        self._first_caller = value

    @property
    def calls(self)-> List[Call]:
        """Return the calls list."""
        return self._calls

    @calls.setter
    def calls(self, value):
        """Validate and assign the calls list."""
        self._calls = []
        # if isinstance(value, str):
        #     value = list(value)
        if not isinstance(value, list):
            raise TypeError('Calls must be a list')
        for call in value:
            if isinstance(call, str):
                if call not in CALLS:
                    raise ValueError(f'{call} is not a valid call')
                call = Call(call)
            self._calls.append(call)

    @property
    def note_keys(self) -> List[str]:
        """Return the note_keys list."""
        return self._note_keys

    @note_keys.setter
    def note_keys(self, value):
        """Assign the note_keys list."""
        self._note_keys = []
        if not isinstance(value, list):
            raise TypeError('Note keys must be a list')
        for key in value:
            if not isinstance(key, str):
                raise TypeError('A note key must be a string')
            self._note_keys.append(key)

    @property
    def notes(self) -> Dict[str, str]:
        """Return the notes dict."""
        return self._notes

    @notes.setter
    def notes(self, value):
        """Assign the notes dict."""
        if not isinstance(value, dict):
            raise TypeError('Notes must be a dict')
        self._note_keys = value
