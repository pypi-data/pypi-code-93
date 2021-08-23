from typing import Dict, List

from pydantic import BaseModel, root_validator

from .. import Annotation, ResponseObject


class TextsResponseObject(BaseModel):
    """
    Object representing a structured piece of text. Recursive.

    Attributes
    ----------
    role: (str, optional) the role of this node in the response
    content:(str, optional) string of translated/transcribed text
    texts: (List[TextsResponseObject], optional) list of same structures, recursive
    score: (int, optional) confidence of response
    features (dict, optional): arbitrary JSON metadata about content
    annotations (Dict[str, List[Annotation]], optional): optional annotations on request
    """

    role: str = None
    content: str = None
    texts: List = None
    score: int = None
    features: dict = None
    annotations: Dict[str, List[Annotation]] = None

    @root_validator()
    def either_content_or_text(cls, values):
        """ "
        validator: ensures either the "content" or "text" fields are present
        """
        content, texts, score = values.get("content"), values.get("texts"), values.get("score")
        if content is None and texts is None:
            raise ValueError('A text response must have either "content" or "texts" fields')
        if texts and score:
            raise ValueError("A branch node should not have a score attached")
        return values

    def auto_content(self):
        if self.features is not None and self.annotations is not None:
            return self.dict()
        if self.content is not None and self.texts is None:
            if self.score is None:
                return self.content
            return {
                "content": self.content,
                "score": self.score,
            }
        if self.content is None and self.texts is not None:
            if len(self.texts) == 1:
                return self.texts[0]
            return self.texts


class TextsResponse(ResponseObject):
    """
    Response consisting of a set of one or more new texts, each with optional annotations attached to it.

    For example a set of possible translations produced by a translation tool or possible transcriptions produced by a
    speech-to-text recogniser.

    Attributes
    ----------
    type (str, required): type of response
    warnings (List[StatusMessage], optional): messages describing any warnings on responses
    texts (List[TextsResponseObject], optional): list of objects representing a structured text response
    """

    type: str = "texts"
    texts: List[TextsResponseObject]

    def auto_content(self):
        if self.warnings is not None:
            return self.dict()
        if len(self.texts) == 1:
            return self.texts[0].auto_content()
        return self.dict()["texts"]
