import string


class Drive(int):
    pass


class ImagePath:
    @staticmethod
    def is_image_path(path):
        return len(path) > 1 and path[0] in string.digits and path[1] == ':'

    @staticmethod
    def split(drive_name, encoding):
        parts = drive_name.split(':', 1)
        if '~' in parts[1]:
            pos = parts[1].rindex('~')
            suffix = parts[1][pos:].encode()
            return int(parts[0]), parts[1][:pos].encode(encoding)+suffix
        return int(parts[0]), parts[1].encode(encoding)

    def name_encoded(self, encoding):
        return self.encoded_name

    def __repr__(self):
        return "ImagePath({}:{})".format(self.drive, self.encoded_name)
