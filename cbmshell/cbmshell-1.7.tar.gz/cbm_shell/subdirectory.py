from cbm_shell.disk_image import DiskImage


class Subdirectory(DiskImage):
    def __init__(self, path, drive):
        self._image = path.subdirectory()
        self.drive = drive
