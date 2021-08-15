import io

from cbm_shell.image_path import ImagePath


class TapImagePathRead(ImagePath):
    def __init__(self, drive, header, data):
        self.drive = drive
        self.header = header
        self.data = data

    @property
    def encoded_name(self):
        return self.header.name

    @property
    def file_type(self):
        return str(self.header.htype)

    @property
    def size_bytes(self):
        return len(self.data)

    def open(self, mode, ftype=None):
        if mode != 'rb':
            raise NotImplementedError('File replacement not supported')
        return io.BytesIO(self.data)

    def exists(self):
        return True

    def name(self, encoding):
        return self.header.name.decode(encoding)

    def unique_name(self, encoding):
        if b'~' in self.header.unique_name and not self.header.unique_name.endswith(b'~'):
            pos = self.header.unique_name.index(b'~')
            suffix = self.header.unique_name[pos:].decode()
            return self.name(encoding)+suffix
        return self.name(encoding)

    def file_info(self, token_set, encoding):
        info = "{}: {}, size={} bytes".format(self.name(encoding), self.file_type, self.size_bytes)
        if self.file_type.startswith('PRG'):
            info += ", start=${:04x}".format(self.header.start)

        return info
