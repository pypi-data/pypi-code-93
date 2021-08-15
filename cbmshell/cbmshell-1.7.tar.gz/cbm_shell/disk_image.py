from d64 import Block
from d64 import DiskImage as D64DiskImage

from cbm_shell.disk_image_path import DiskImagePath


class DiskImage:
    @staticmethod
    def is_valid_image(filepath):
        return D64DiskImage.is_valid_image(filepath)

    def __init__(self, path, mode, drive):
        self.drive = drive
        self._image = D64DiskImage(path).open(mode)

    @property
    def writeable(self):
        return self._image.writeable

    def close(self):
        self._image.close()

    def path(self, name):
        return DiskImagePath(self.drive, self._image.path(name))

    def glob(self, name):
        for path in self._image.glob(name):
            yield DiskImagePath(self.drive, path)

    def expand(self, name):
        yield from self.glob(name+b'*')

    def create_partition(self, name, start_track, num_blocks):
        part = self._image.partition(name)
        part.create(Block(self._image, start_track, 0), num_blocks)
        return part

    def directory(self, **kwargs):
        yield from self._image.directory(**kwargs)

    def __str__(self):
        return self._image.__str__()
