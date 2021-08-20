from abc import abstractmethod
from .module import ModuleProvider
from .proto import ProtoShell, ProtoCmd
from .config import Config


class FolderProvider(ModuleProvider):

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_path(self):
        pass

    @abstractmethod
    def is_folder(self):
        pass

    @abstractmethod
    def get_children(self):
        pass

    @abstractmethod
    def get_child(self, name):
        pass

    @abstractmethod
    def get_stat(self):
        pass

    @abstractmethod
    def get_hash(self):
        pass

    @abstractmethod
    def create_folder(self, name):
        pass

    @abstractmethod
    def create_file(self, name, data, binary=True):
        pass

    @abstractmethod
    def get_data(self, binary=True):
        pass

    @abstractmethod
    def delete(self, name):
        pass


class Folder(ProtoShell):

    class Copy(ProtoCmd):

        def __init__(self):
            super().__init__('copy',
                             'copy from source_path to target_path')

        def add_arguments(self, parser):
            parser.add_argument('source_path', help="specifies the source_path")
            parser.add_argument('target_path', help="specifies the target_path")

        def run(self, args):
            Folder.from_path(args.source_path).copy(Folder.from_path(args.target_path))

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get',
                             'download folder or file from path')

        def add_arguments(self, parser):
            parser.add_argument('path', help="specifies the path")
            parser.add_argument('--local_path', help="specifies the local path where to save", default='.')

        def run(self, args):
            Folder.from_path(args.path).get(args.local_path)

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put',
                             'upload folder or file to path')

        def add_arguments(self, parser):
            parser.add_argument('local_path', help="specifies the local path to upload")
            parser.add_argument('target_path', help="specifies the target path")

        def run(self, args):
            Folder.from_path(args.target_path).put(args.local_path)

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create',
                             'create folder or file on path')

        def add_arguments(self, parser):
            parser.add_argument('op', choices=['folder', 'file'],
                                help="specifies whether to create folder (default) or file", default='folder', const='folder', nargs='?')
            parser.add_argument('target_path', help="specifies the target path")
            parser.add_argument('name', help="specifies the name of the folder or file to be created")

        def run(self, args):
            if args.op == 'folder':
                Folder.from_path(args.target_path).create_folder(args.name)
            else:
                Folder.from_path(args.target_path).create_file(args.name)

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete',
                             'delete path')

        def add_arguments(self, parser):
            parser.add_argument('path', help="specifies the path to be deleted")

        def run(self, args):
            Folder.from_path(args.path).delete()

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list',
                             'list files and folders on path')

        def add_arguments(self, parser):
            parser.add_argument('path', help="specifies the path to be listed", default=None, const=None, nargs='?')

        def run(self, args):
            if args.path:
                if args.path:

                    folder = Folder.from_path(args.path)
                    for c in folder.get_children():
                        print(c.get_name())
                else:
                    for mount in Config.init().list_entries('mounts'):
                        print(mount['name'])
            else:
                for mount in Config.init().list_entries('mounts'):
                    print(mount['name'])

    class Checksum(ProtoCmd):

        def __init__(self):
            super().__init__('checksum',
                             'calculate the checksum of the folder at path')

        def add_arguments(self, parser):
            parser.add_argument('path', help="specifies the path to be deleted")

        def run(self, args):
            print(Folder.from_path(args.path).get_hash())

    def __init__(self):
        super().__init__('folder', [Folder.Create(), Folder.Copy(), Folder.Get(), Folder.Put(), Folder.Delete(), Folder.List(), Folder.Checksum()], 'folder shell')

    @classmethod
    def from_path(cls, path):
        config = Config.init()
        mount_path = '/{0}'.format(path.split('/')[1])
        folder_path = '/'.join(path.split('/')[2:])
        mount = config.get_entry_instance('mounts', mount_path)
        return mount.get_folder(folder_path)

    @classmethod
    def copy(cls, source, dest):
        if source.is_folder():
            target = dest.create_folder(source.get_name())
            children = source.get_children()

            for file in [c for c in children if not c.is_folder()]:
                target.create_file(file.get_name(), file.get_data())

            for folder in [c for c in children if c.is_folder()]:
                Folder.copy(folder, target)
        else:
            dest.create_file(source.get_name(), source.get_data())

    @classmethod
    def match(cls, source, dest):
        return source.get_hash() == dest.get_hash()
