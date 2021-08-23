from pydantic import BaseModel

from .ResponseObject import ResponseObject


class Response(BaseModel):
    """
    Representation of a successful completion response.

    Abstract, subclasses should instantiate this with their own type

    Attributes
    ----------
    response (ResponseObject, required):
    """

    response: ResponseObject
