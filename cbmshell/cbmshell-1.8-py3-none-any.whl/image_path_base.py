
class ImagePathBase:
    def __init__(self, drive, path):
        self.drive = drive
        self._path = path

    def __repr__(self):
        return "ImagePath({}:{})".format(self.drive, self._path.name)
