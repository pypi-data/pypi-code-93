import io
import struct

from cbm_shell.image_path import ImagePath
from tap_file import TapHeader, TapProgram, TapSeqData, HeaderType


class FileData(io.BytesIO):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def close(self):
        self.path.write_data()
        super().close()


class TapImagePath(ImagePath):
    def __init__(self):
        self.record_len = None

    @classmethod
    def from_entry(cls, image, header, data):
        """Create instance from existing image entry."""
        this = cls()
        this.image = image
        this.header = header
        this.data = data
        this._unique_name = None
        this.encoded_name = header.name
        this._file_type = header.htype
        return this

    @classmethod
    def new(cls, image, name):
        """Create instance for non-existent entry."""
        this = cls()
        this.image = image
        this._unique_name = name
        if b'~' in name:
            name, _ = name.rsplit(b'~', 1)
        this.encoded_name = name
        this._file_type = None
        this.header = None
        this.data = None
        return this

    @property
    def drive(self):
        return self.image.drive

    @property
    def file_type(self):
        if self._file_type is None:
            raise FileNotFoundError("File not found: "+str(self._unique_name))

        return str(self._file_type)

    @property
    def size_bytes(self):
        if self.data is None:
            raise FileNotFoundError("File not found: "+str(self._unique_name))

        return len(self.data)

    def open(self, mode, ftype=None, record_len=None):
        if mode == 'rb':
            if self.data is None:
                raise FileNotFoundError("File not found: "+str(self._unique_name))

            return io.BytesIO(self.data)

        # file write
        if ftype not in ('PRG', 'PRG_RELOC', 'SEQ'):
            raise ValueError("Invalid file type: "+str(ftype))
        self._file_type = ftype
        self.data = FileData(self)

        return self.data

    def write_data(self):
        objs = []
        data = self.data.getvalue()
        if self._file_type == 'SEQ':
            objs.append(TapHeader(HeaderType.SEQ, self.encoded_name))
            while True:
                chunk = data[:TapSeqData.MAX_DATA]
                if len(chunk) < TapSeqData.MAX_DATA:
                    # end of file
                    objs.append(TapSeqData(chunk+b'\x00'))
                    break
                objs.append(TapSeqData(chunk))
                data = data[TapSeqData.MAX_DATA:]
        else:
            htype = HeaderType.PRG if self._file_type == 'PRG' else HeaderType.PRG_RELOC
            start_addr, = struct.unpack('<H', data[:2])
            end_addr = start_addr+len(data)-2
            objs.append(TapHeader(htype, self.encoded_name, start=start_addr, end=end_addr))
            objs.append(TapProgram(data[2:]))

        self.image.append_objs(objs)

    def exists(self):
        return self.header is not None

    def is_file(self):
        return True

    def name(self, encoding):
        return self.encoded_name.decode(encoding)

    def unique_name(self, encoding):
        if self._unique_name:
            return self._unique_name.decode(encoding)

        if b'~' in self.header.unique_name and not self.header.unique_name.endswith(b'~'):
            pos = self.header.unique_name.index(b'~')
            suffix = self.header.unique_name[pos:].decode()
            return self.name(encoding)+suffix
        return self.name(encoding)

    def file_info(self, token_set, encoding):
        if self.header is None:
            raise FileNotFoundError("File not found: "+str(self._unique_name))

        info = "{}: {}, size={} bytes".format(self.name(encoding), self.file_type, self.size_bytes)
        if self.file_type.startswith('PRG'):
            info += ", start=${:04x}".format(self.header.start)

        return info

    def unlink(self):
        raise NotImplementedError("Cannot remove files from .tap images")
