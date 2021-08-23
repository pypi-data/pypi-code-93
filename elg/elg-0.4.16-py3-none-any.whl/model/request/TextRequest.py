from pathlib import Path
from typing import Dict, List

from pydantic import validator

from .. import Annotation, Request


class TextRequest(Request):
    """
    Request representing a single piece of text, optionally with associated markup

    For example a list of paragraphs or sentences, or a corpus of documents, each divided into sentences.
    While this could be represented as standoff annotations in a plain "text" request, the structured format is more
    suitable for certain types of tools.

    Attributes
    ----------
    type (str, required): the type of request. must be "text"
    params (Dict, optional): vendor specific requirements
    content: (str, optional) text content
    mimeType: (str, optional) mime type of request, default text/plain
    features (Dict, optional): arbitrary json metadata about content
    annotations (Dict[str, List[Annotation]], optional): optional annotations on request
    """

    type: str = "text"
    content: str
    mimeType: str = "text/plain"
    features: Dict = None
    annotations: Dict[str, List[Annotation]] = None

    @classmethod
    def from_file(cls, filename, features: Dict = None, annotations: Dict[str, List[Annotation]] = None):
        filename = Path(filename)
        if not filename.is_file():
            raise ValueError(f"{filename} musts be the path to a file.")
        with open(filename) as f:
            content = f.read()
        return cls(
            content=content,
            features=features,
            annotations=annotations,
        )
