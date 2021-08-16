import os.path


class PC64File:
    PC64_MAGIC = b'C64File\x00'

    @staticmethod
    def is_valid_image(filepath):
        with filepath.open('rb') as fileh:
            magic = fileh.read(len(PC64File.PC64_MAGIC))

        return magic == PC64File.PC64_MAGIC

    def __init__(self, fileh):
        if fileh.read(len(self.PC64_MAGIC)) != self.PC64_MAGIC:
            raise ValueError("Invalid file format")

        header = fileh.read(0x12)
        if len(header) != 0x12:
            raise ValueError("Invalid file format")

        self.name = header[:0x10].rstrip(b'\x00')
        self.record_len = header[0x11]

        if self.record_len:
            self.file_type = 'REL'
        elif hasattr(fileh, 'name'):
            _, ext = os.path.splitext(fileh.name)
            type_map = {'P': 'PRG', 'S': 'SEQ', 'U': 'USR'}
            self.file_type = type_map.get(ext[1].upper())
        else:
            self.file_type = None
