from __future__ import annotations

from typing import Dict, List, Text

from pydantic import BaseModel, root_validator

from .. import Annotation, Request


class Text(BaseModel):
    """
    A single node in a structured text request.

    Each text can have an associated score (for example a confidence value for multiple alternative translations or
    transcriptions) and optional annotations, which can be linked to both the result text in this object and to the
    original source material from the corresponding request.

    Attributes
    ----------
    content: (str, optional) text content
    mime_type: (str, optional) mime type of request, default text/plain
    features (dict, optional) arbitrary json metadata about content
    annotations (Dict[str, List[Annotation]], optional): optional annotations on request
    texts: (List[Text], optional): recursive, same structure again
    """

    content: str = None
    mime_type: str = "text/plain"
    features: dict = None
    annotations: Dict[str, List[Annotation]] = None
    texts: List[Text] = None

    @root_validator()
    def either_content_or_text(cls, values):
        """
        validator: ensures only either the "content" or the "text" fields are present
        """
        content, texts = values.get("content"), values.get("texts")
        if content is None and texts is None:
            raise ValueError('A structured text request must have either "content" or "texts" fields')
        if content:
            values["mimeType"] = "text/plain"
        else:
            values["mimeType"] = None
        return values


class StructuredTextRequest(Request):
    """
    Request representing text with some structure,

    For example a list of paragraphs or sentences, or a corpus of documents, each divided into sentences.
    While this could be represented as standoff annotations in a plain "text" request, the structured format is more
    suitable for certain types of tools.

    Attributes
    ----------
    type (str, required): the type of request. must be "audio"
    params (dict, optional): vendor specific requirements
    texts: (List[Text], required): the actual text object with the text content
    """

    type: str = "structuredText"
    texts: List[Text]
