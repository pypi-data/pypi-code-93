from typing import List

from pydantic import BaseModel, Field

from .. import ResponseObject


class ClassesResponse(BaseModel):
    """
    Classification object: classification and score (optional likelihood of classification)

    Attributes
    ----------
    class: (str, required) labelled class
    score: (float, optional) confidence score in class
    """

    class_field: str = Field(None, alias="class")
    score: float = None


class ClassificationResponse(ResponseObject):
    """
    Response encapsulating one or more classifications of the whole input message, optionally with confidence scores
    attached.

    Attributes
    ----------
    type (string, required): type of response
    warnings (List[StatusMessage], optional): messages describing any warnings on responses
    classes: (List[ClassesResponse], optional) : list of classications, zero or more allowed
    """

    type: str = "classification"
    classes: List[ClassesResponse] = None

    def auto_content(self):
        if self.warnings is not None:
            return self.dict()
        if len(self.classes) == 1:
            return self.classes[0].dict()
        return self.dict()["classes"]
