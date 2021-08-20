from pynecone import MountProvider, FolderProvider

import os
import hashlib


class Folder(FolderProvider):

    def get_instance(self, **kwargs):
        pass

    def __init__(self, mount, path):
        self.mount = mount
        self.path = path

    def get_name(self):
        return self.path.split('/')[-1]

    def get_path(self):
        return '{0}/{1}'.format(self.mount, '/'.join(self.path.split('/')[1:]))

    def is_folder(self):
        return os.path.isdir(self.path)

    def get_children(self):
        if os.path.isdir(self.path):
            for f in os.listdir(self.path):
                yield Folder(self.mount, '{0}/{1}'.format(self.path, f))

    def get_child(self, name):
        if os.path.isdir(self.path):
            for f in os.listdir(self.path):
                if name == f:
                    return Folder(self.mount, '{0}/{1}'.format(self.path, f))
        return None

    def get_hash(self):
        if os.path.isfile(self.path):
            with open(self.path, "rb") as f:
                file_hash = hashlib.md5()
                while True:
                    data = f.read(8192)
                    if not data:
                        break
                    else:
                        file_hash.update(data)
                file_hash.update(self.path.split('/')[-1].encode('utf-8'))
                return file_hash.hexdigest()
        else:
            folder_hash = hashlib.md5()
            for c in self.get_children():
                folder_hash.update(c.get_hash().encode('utf-8'))
            folder_hash.update(self.path.split('/')[-1].encode('utf-8'))
            return folder_hash.hexdigest()

    def get_stat(self):
        return os.stat(self.path)

    def create_folder(self, name):
        if self.is_folder():
            fp = '{0}/{1}'.format(self.path, name)
            os.mkdir(fp)
            return Folder(self.mount, fp)
        else:
            return None

    def create_file(self, name, data, binary=True):
        if self.is_folder():
            target_path = '{0}/{1}'.format(self.path, name)
            with open(target_path, 'wb' if binary else 'w') as f:
                f.write(data)
            return Folder(self.mount, target_path)
        else:
            return None

    def get_data(self, binary=True):
        with open(self.path, 'rb' if binary else 'r') as f:
            return f.read()

    def delete(self):
        if self.is_folder():
            os.rmdir(self.path)
            return True
        else:
            os.remove(self.path)
            return True
        return False


class Module(MountProvider):

    def get_instance(self, **kwargs):
        return Module(**kwargs)

    def __init__(self, **kwargs):
        self.cfg = kwargs

    def get_folder(self, path):
        return Folder(self.cfg['name'], '{0}/{1}'.format(self.cfg['path'], path))





