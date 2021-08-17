from typing import Tuple, Iterator

from pydantic import BaseModel, validator


class _BaseModelConfig(BaseModel):
    class Config:
        validate_all = True
        validate_assignment = True
        extra = "forbid"
        allow_mutation = False


class Verse(_BaseModelConfig):
    quote: str
    authors: Tuple[str, ...]

    @validator("authors", pre=True)
    def split_str(cls, value):
        if isinstance(value, str):
            return tuple(map(lambda author: author.strip(), value.split(",")))
        return value


class MahabharataPoems(_BaseModelConfig):
    __root__: Tuple[Verse, ...]

    def verse_by_speaker(self, author) -> Verse:
        return next((verse for verse in self if author in verse.authors), None)

    def __iter__(self) -> Iterator[Verse]:
        return iter(self.__root__)

    def __getitem__(self, item) -> Verse:
        return self.__root__[item]

    def __len__(self) -> int:
        return len(self.__root__)
