from base64 import b64decode
from pathlib import Path
from typing import Dict, List

from pydantic import validator

from .. import Annotation, ResponseObject


class AudioResponse(ResponseObject):
    """
    Response representing audio data with optional standoff annotations (e.g. text-to-speech results)

    Attributes
    ----------
    type (string, required): type of response
    warnings (List[StatusMessage], optional): messages describing any warnings on responses
    content (str, required): base64 encoded audio for short audio snippets
    format (str, required): specifies audio format used: either "LINEAR16" or "MP3"
    features (dict, optional): arbitrary json metadata about content
    annotations (Dict[str, List[Annotation]], optional): optional annotations on request
    """

    type: str = "audio"
    content: str
    format: str
    features: dict = None
    annotations: Dict[str, List[Annotation]] = None

    @validator("format")
    def format_must_be_specific(cls, v):
        """
        validator: ensures the format of the audio response is either "LINEAR16" or "MP3"
        """
        acceptable_formats = ["LINEAR16", "MP3"]
        if v.lower() not in acceptable_formats:
            raise ValueError("The format given is not supported")
        return v.lower()

    def to_file(self, filename):
        filename = Path(filename)
        with open(filename, "wb") as f:
            f.write(b64decode(self.content))

    def auto_content(self):
        if self.warnings is not None:
            return self.dict()
        if self.features is not None:
            return self.dict()
        if self.annotations is not None:
            return self.dict()
        return {
            "content": self.dict()["content"],
            "format": self.dict()["format"],
        }
