from cbm_files import ProgramFile

from cbm_shell.image_path import ImagePath


class DiskImagePath(ImagePath):
    def __init__(self, drive, path):
        self.drive = drive
        self._path = path

    @classmethod
    def glob(cls, drive, name, image):
        return [cls(drive, p) for p in image.glob(name)]

    @classmethod
    def expand(cls, drive, name, image):
        return [cls(drive, p) for p in image.glob(name+b'*')]

    @property
    def encoded_name(self):
        return self._path.name

    @property
    def file_type(self):
        return self._path.entry.file_type

    @property
    def size_bytes(self):
        return self._path.size_bytes

    @property
    def record_len(self):
        return self._path.entry.record_len

    def open(self, mode, ftype=None, record_len=None):
        ftype = ftype[:3] if ftype else None
        return self._path.open(mode, ftype, record_len)

    def unlink(self):
        return self._path.unlink()

    def exists(self):
        return self._path.exists()

    def lock(self):
        self._path.entry.protected = True

    def unlock(self):
        self._path.entry.protected = False

    def name(self, encoding):
        return self._path.name.decode(encoding)

    def subdirectory(self):
        return self._path.image.subdirectory(self._path.name)

    unique_name = name

    def file_info(self, token_set, encoding):
        info = "{}: {}, size={} bytes".format(self.name(encoding), self.file_type, self.size_bytes)

        if self.file_type == 'PRG':
            with self.open('rb') as fileh:
                prg = ProgramFile(fileh, token_set, encoding)
            if prg:
                info += ", start=${:04x}".format(prg.start_addr)
            elif self.file_type == 'REL':
                info += ", record={} bytes".format(self.record_len)

        return info
