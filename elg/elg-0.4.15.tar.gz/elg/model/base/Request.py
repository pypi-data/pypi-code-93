from pydantic import BaseModel


class Request(BaseModel):
    """
    Representation of a service invocation request

    Intended to be abstract, subclasses should be initiated with their specific type

    Subclasses
    ----------
    request.AudioRequest
    request.TextRequest
    request.StructuredTextRequest

    Attributes
    ----------
    type (str, required on subclass instantiation): the type of request
    params (dict, optional): vendor specific requirements
    """

    type: str = None
    params: dict = None

    def __str__(self):
        return " - ".join([f"{k}: {v}" for k, v in self.dict().items() if v is not None])
