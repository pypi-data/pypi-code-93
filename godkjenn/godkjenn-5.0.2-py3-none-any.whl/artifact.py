from pathlib import Path


class Artifact:
    """A single received or accepted piece of data.

    An artifact includes the path to the file itself as well as
    its metadata.
    """

    def __init__(self, path: Path, mime_type, encoding=None):
        self._path = path
        self._mime_type = mime_type
        self._encoding = encoding

    @property
    def path(self):
        "Path to the file containing the artifact's data."
        return self._path

    @property
    def mime_type(self):
        "MIME-type for the artifact."
        return self._mime_type

    @property
    def encoding(self):
        "Encoding of text data (if any)."
        return self._encoding

    def __eq__(self, rhs):
        return all(
            (self.path == rhs.path, self.mime_type == rhs.mime_type, self.encoding == rhs.encoding),
        )
