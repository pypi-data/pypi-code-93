from typing import Generator, Dict, Set
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ... import validate
from ...Token import Token
from ...MemberAdapter.MemberAdapter import MemberAdapter

from .TokenHandlerStrategy import TokenHandlerStrategy


def token_id_generator() -> Generator[int, None, None]:
    """Generates a new token id each call"""
    token_id = 0
    while True:
        yield token_id
        token_id += 1


class BasicTokenHandlerStrategy(TokenHandlerStrategy):
    """Maintains an active list of tokens that are in use"""

    def __init__(self, scheduler: AsyncIOScheduler):
        self._scheduler = scheduler
        self._id_generator = token_id_generator()
        self._tokens: Dict[int, Token] = {}

    def get_token(self, token_id: int) -> Token:
        return self._tokens[token_id]

    def get_tokens(self, member: MemberAdapter) -> Set[int]:
        tokens = set()
        for token_id, token in self._tokens.items():
            if not validate(token.author, member):
                continue
            tokens.add(token_id)
        return tokens

    def add_token(self, token: Token, duration: float):
        token_id = next(self._id_generator)
        self._tokens.update({token_id: token})

        # Schedule the Token for deletion after the duration specified.
        self._scheduler.add_job(
            lambda tid=token_id, *_: self._do_token_job(tid), "interval", seconds=5, id=f"token_{token_id}"
        )
        self._scheduler.start()

    def use_token(self, token_id: int):
        token = self._tokens[token_id]
        token.uses -= 1
        if token.uses == 0:
            self.del_token(token_id)

    def _do_token_job(self, token_id: int):
        """
        Deletes a token and its job from the Scheduler, to prevent it calling this method multiple times.

        Parameters
        ----------
        token_id : int
            The Token ID to be deleted.
        """
        self._scheduler.remove_job(f"token_{token_id}")
        self.del_token(token_id)

    def del_token(self, token_id: int):
        del self._tokens[token_id]
