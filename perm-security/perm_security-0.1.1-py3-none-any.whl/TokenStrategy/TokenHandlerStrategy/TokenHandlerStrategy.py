from typing import Set
from abc import ABC, abstractmethod

from ...Token import Token
from ...MemberAdapter.MemberAdapter import MemberAdapter


class TokenHandlerStrategy(ABC):
    """Maintains an active list of tokens that are in use"""

    @abstractmethod
    def get_token(self, token_id: int) -> Token:
        """
        Finds a Token from the ID provided.

        Parameters
        ----------
        token_id : int
            The ID of the respective Token.

        Returns
        -------
        Token
            The Token that corresponds to the Token.
        """

    @abstractmethod
    def get_tokens(self, member: MemberAdapter) -> Set[int]:
        """
        Retrieves a Set of Token IDs that are valid for the Member provided.

        Parameters
        ----------
        member : MemberAdapter
            The Member that we are getting the Tokens for.

        Returns
        -------
        Set[int]
            A Set of all the Token IDs that a Member can use.
        """

    @abstractmethod
    def add_token(self, token: Token, duration: float):
        """
        Adds a Token to the Set of all active Tokens for a duration specified.

        Parameters
        ----------
        token : Token
            The Token to be added and managed by this class.
        duration : float
            The duration that this Token should exist inside this class for.
        """

    @abstractmethod
    def use_token(self, token_id: int):
        """
        Uses a Token a single time.  If the Token has no more uses, then it will be deleted.

        Parameters
        ----------
        token_id : int
            The ID of the Token to be used.
        """

    @abstractmethod
    def del_token(self, token_id: int):
        """
        Removes a Token from the Set of all active Tokens inside this class.

        Parameters
        ----------
        token_id : int
            The ID of the Token to be deleted.
        """
