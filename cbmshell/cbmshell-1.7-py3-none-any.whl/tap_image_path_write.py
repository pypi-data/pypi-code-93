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


class TapImagePathWrite(ImagePath):
    def __init__(self, image, name):
        self.image = image
        self._unique_name = name
        if b'~' in name:
            name, _ = name.rsplit(b'~', 1)
        self.encoded_name = name

    @property
    def drive(self):
        return self.image.drive

    def open(self, mode, ftype, record_len=None):
        if mode != 'wb':
            raise FileNotFoundError("File not found: "+str(self._unique_name))
        if ftype not in ('PRG', 'PRG_RELOC', 'SEQ'):
            raise ValueError("Invalid file type: "+str(ftype))
        self.file_type = ftype
        self.data = FileData(self)

        return self.data

    def write_data(self):
        objs = []
        data = self.data.getvalue()
        if self.file_type == 'SEQ':
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
            htype = HeaderType.PRG if self.file_type == 'PRG' else HeaderType.PRG_RELOC
            start_addr, = struct.unpack('<H', data[:2])
            end_addr = start_addr+len(data)-2
            objs.append(TapHeader(htype, self.encoded_name, start=start_addr, end=end_addr))
            objs.append(TapProgram(data[2:]))

        self.image.append_objs(objs)

    def exists(self):
        return False

    def is_file(self):
        return True

    def name(self, encoding):
        return self.encoded_name.decode(encoding)

    def unique_name(self, encoding):
        return self._unique_name.decode(encoding)

    def file_info(self, token_set, encoding):
        raise FileNotFoundError("File not found: "+str(self._unique_name))
