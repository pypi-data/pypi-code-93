from typing import List

from pydantic import BaseModel

from .StatusMessage import StatusMessage


class ResponseObject(BaseModel):
    """
    Representation of a successful completion response.

    Abstract, subclasses should instantiate this with their own type
    Subclasses
    ----------
    response.AnnotationsResponse
    response.AudioResponse
    response.ClassificationResponse
    response.StoredResponse
    response.TextsResponse

    Attributes
    ----------
    type (string, required on subclass): type of response
    warnings (List[StatusMessage], optional): messages describing any warnings on responses
    """

    type: str
    warnings: List[StatusMessage] = None
