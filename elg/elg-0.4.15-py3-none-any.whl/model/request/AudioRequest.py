from pathlib import Path
from typing import Dict, List

from pydantic import validator

from .. import Annotation, Request


class AudioRequest(Request):
    """
    Request representing a piece of audio - the actual audio data will be sent as a separate request.

    Subclass of Request

    Attributes
    ----------
    type (str, required): the type of request. must be "audio"
    params (dict, optional): vendor specific requirements
    format (str, required): the format of the audio request
    sampleRate (int, required): sample rate of audio
    features (dict, optional): arbitrary json metadata about content
    annotations (Dict[str, List[Annotation]], optional): optional annotations on request
    """

    type: str = "audio"
    content: bytes = None
    format: str = "LINEAR16"
    sample_rate: int = None
    features: Dict = None
    annotations: Dict[str, List[Annotation]] = None

    @validator("format")
    def format_must_be_specific(cls, v):
        """
        validator: ensures the format of the audio request is either "LINEAR16" or "MP3"
        """
        acceptable_formats = ["LINEAR16", "MP3"]
        v = v.upper()
        if v not in acceptable_formats:
            raise ValueError("The format given is not supported")
        return v

    @classmethod
    def from_file(
        cls,
        filename,
        format: str = None,
        sample_rate: int = None,
        features: Dict = None,
        annotations: Dict[str, List[Annotation]] = None,
    ):
        filename = Path(filename)
        if not filename.is_file():
            raise ValueError(f"{filename} musts be the path to a file.")
        with open(filename, "rb") as f:
            content = f.read()
        if format is None:
            format = "MP3" if filename.suffix == ".mp3" else "LINEAR16"
        return cls(
            content=content,
            format=format,
            sample_rate=sample_rate,
            features=features,
            annotations=annotations,
        )

    def __str__(self):
        return " - ".join([f"{k}: {v}" for k, v in self.dict().items() if v is not None and k != "content"])
