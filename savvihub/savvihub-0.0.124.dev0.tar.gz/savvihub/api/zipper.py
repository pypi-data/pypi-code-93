import os
import zipfile


class Zipper(zipfile.ZipFile):
    def __init__(self, file, mode):
        super(Zipper, self).__init__(file, mode)

    @classmethod
    def zipdir(cls, path, ziph):
        for root, dirs, files in os.walk(path):
            files = [f for f in files if not f.startswith('.')]
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))
