import random
import uuid
from typing import Any, Sequence, Set
from uuid import UUID


def random_float(end: float, start: float = 0.0):
    return random.uniform(start, end)


# TODO: deprecate in favor of random_unique_items
def get_unique_randoms(iterable: Sequence, count: int) -> Set[str]:
    return set([i.symbol for i in list(random_unique_items(iterable=iterable, count=count))])


def random_unique_items(iterable: Sequence, count: int) -> Set[Any]:
    return set(random.choices(iterable, k=min(len(iterable), count)))


def get_uuid() -> UUID:
    return uuid.uuid4()
