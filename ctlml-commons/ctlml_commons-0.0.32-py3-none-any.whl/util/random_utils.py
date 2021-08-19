import random
import uuid
from typing import Sequence, Set
from uuid import UUID


def random_float(end: float, start: float = 0.0):
    return random.uniform(start, end)


def get_unique_randoms(iterable: Sequence, count: int) -> Set[str]:
    indices: Set[str] = set()
    num_items: int = min(len(iterable), count)

    while len(indices) < num_items:
        indices.add(random.choice(iterable).symbol)

    return indices


def get_uuid() -> UUID:
    return uuid.uuid4()
