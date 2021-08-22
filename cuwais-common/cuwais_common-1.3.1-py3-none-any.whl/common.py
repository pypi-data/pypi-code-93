import hashlib
from enum import Enum, unique


@unique
class Outcome(Enum):
    Win = 1
    Loss = 2
    Draw = 3


@unique
class Result(Enum):
    ValidGame = "valid-game"
    Exception = "exception"
    IllegalMove = "illegal-move"
    IllegalBoard = "illegal-board"
    BrokenEntryPoint = "broken-entry-point"
    UnknownResultType = "unknown-result-type"
    GameUnfinished = "game-unfinished"
    Timeout = "timeout"
    ProcessKilled = "process-killed"


def calculate_git_hash(user_id: int, commit_hash: str, url: str) -> str:
    m = hashlib.sha256()
    m.update(str(user_id).encode('utf-8'))
    m.update(commit_hash.encode('utf-8'))
    # m.update(url.encode('utf-8'))
    return str(m.hexdigest())
