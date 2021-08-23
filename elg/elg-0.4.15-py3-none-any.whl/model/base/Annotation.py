from typing import Dict, List

from pydantic import BaseModel


class Annotation(BaseModel):
    """
    Representation of a single annotation with respect to either one or two streams of data.

    Attributes
    ----------
    start (int, required): annotation start location (in response)
    end (int, required): annotation end location (in response)
    source_start (int, required in cases): annotation start location (in source)
    source_end (int, required in cases): annotation end location (in source)
    features (dict, optional): arbitrary json metadata about content
    """

    start: int
    end: int
    sourceStart: int = None
    sourceEnd: int = None
    features: dict = None
