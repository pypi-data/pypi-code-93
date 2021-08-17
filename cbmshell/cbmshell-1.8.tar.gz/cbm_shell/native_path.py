from pathlib import Path

from cbm_files import PC64File, ProgramFile


class NativePath:
    def __init__(self, path_name):
        self.path = Path(path_name)
        self.name = self.path.name
        if self.path.is_file() and PC64File.is_valid_image(self.path):
            with self.path.open('rb') as fileh:
                self.is_pc64 = True
                pcf = PC64File(fileh)
                self.encoded_name = pcf.name
                self.file_type = pcf.file_type
                self.record_len = pcf.record_len
        else:
            self.is_pc64 = False
            self.file_type = 'PRG' if self.path.is_file() else None
            self.record_len = None

    def file_info(self, token_set, encoding):
        if self.path.is_file():
            fname = self.encoded_name if self.is_pc64 else self.path
            info = "{!s}: {}".format(fname, self.file_type)
            if self.file_type == 'PRG':
                with self.open('rb') as fileh:
                    prg = ProgramFile(fileh, token_set, encoding)
                    if prg:
                        info += ", start=${:04x}".format(prg.start_addr)
            elif self.record_len:
                info += ", record={} bytes".format(self.record_len)
            return info

        return "Skipping non-file path {!s}".format(self.path)

    def name_encoded(self, encoding):
        if self.is_pc64:
            return self.encoded_name
        return self.name.encode(encoding)

    def as_path(self):
        return self.path

    def is_file(self):
        return self.path.is_file()

    def is_dir(self):
        return self.path.is_dir()

    def exists(self):
        return self.path.exists()

    def open(self, mode, **kwargs):
        fileh = self.path.open(mode)
        if self.is_pc64:
            _ = PC64File(fileh)
        return fileh

    def unlink(self):
        return self.path.unlink()

    def __str__(self):
        return str(self.path)
