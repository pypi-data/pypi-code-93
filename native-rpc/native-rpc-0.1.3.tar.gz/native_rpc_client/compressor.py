from gzip import GzipFile
from typing import BinaryIO


class Compressor:
    def __init__(self):
        pass

    @property
    def content_encoding(self) -> str:
        return ''

    def compress(self, reader: BinaryIO, writer: BinaryIO) -> None:
        pass


class GZipCompressor(Compressor):
    def __init__(self, compress_level=9):
        super(GZipCompressor, self).__init__()
        self._compress_level = compress_level

    @property
    def content_encoding(self) -> str:
        return 'gzip'

    def compress(self, reader: BinaryIO, writer: BinaryIO) -> None:
        with GzipFile(fileobj=writer, mode='w', compresslevel=self._compress_level) as f:
            f.write(reader.read())
