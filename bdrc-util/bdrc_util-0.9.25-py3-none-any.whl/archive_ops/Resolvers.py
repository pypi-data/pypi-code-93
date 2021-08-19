from enum import Enum


class Resolvers(Enum):
    DEFAULT = 1,
    TWO = 2,        # last two of label
    S3_BUCKET = 3,  # to resolve bdrcIIIF viewer
    NULL = 4        # No transform, just append