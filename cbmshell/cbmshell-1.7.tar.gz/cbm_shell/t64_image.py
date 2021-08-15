from collections import defaultdict

import t64

from cbm_shell.t64_image_path import T64ImagePath


class T64Image:
    @staticmethod
    def is_valid_image(file_path):
        return t64.is_valid_image(file_path)

    def __init__(self, filepath, drive):
        self.drive = drive
        self.filepath = filepath
        self.writeable = False
        self.image = t64.T64ImageReader(filepath)
        self.image.open()

        name_count = defaultdict(int)
        for entry in self.image.iterdir():
            suffix = "~{}".format(name_count[entry.name] if name_count[entry.name] else '')
            if suffix == '~' and entry.name:
                suffix = ''
            entry.unique_name = entry.name+suffix.encode()
            name_count[entry.name] += 1

    def close(self):
        self.image.close()

    def path(self, name):
        for entry in self.image.iterdir():
            if entry.unique_name == name:
                return T64ImagePath(self.drive, entry)
        raise FileNotFoundError("File not found: "+str(name))

    def glob(self, name):
        return []

    def expand(self, name):
        for entry in self.image.iterdir():
            if entry.unique_name.startswith(name):
                yield T64ImagePath(self.drive, entry)

    def directory(self, pattern=b'', encoding='petscii-c64en-uc', drive=0):
        yield from self.image.directory(pattern, encoding, drive)

    def __str__(self):
        return "T64Image({!s})".format(self.filepath)
