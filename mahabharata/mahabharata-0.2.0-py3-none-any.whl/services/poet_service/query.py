from typing import Set, Optional, Tuple

from mahabharata.models.poem import Verse
from . import POEMS


def list_all_authors() -> Set[str]:
    return {author for verse in POEMS for author in verse.authors}


def list_all_collaborators(author: str) -> Set[str]:
    return {
        collaborator
        for verse in POEMS
        for collaborator in verse.authors
        if author in verse.authors and collaborator != author
    }


def get_verse_from_author(author: str) -> Optional[Verse]:
    try:
        return POEMS.verse_by_speaker(author)
    except:
        return None


def all_verses() -> Tuple[Verse, ...]:
    return POEMS


def get_all_verses_by_author(author: str) -> Tuple[Verse, ...]:
    return tuple(verse for verse in POEMS if author in verse.authors)
