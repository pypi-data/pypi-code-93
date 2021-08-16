import os
import datetime
from time import time
from uuid import uuid4
import json
import inspect
from Util.JobHelper import debug, get_stack_frame
import tarfile


class DumperHelper:
    def __init__(self, **kwargs):
        run_date = kwargs.get('run_date', datetime.datetime.now())
        date_folder = kwargs.get('date_folder', run_date.strftime('%Y-%m-%d'))
        self.category = kwargs.get('category', '')

        if kwargs.get('file_folder'):
            self.file_folder = kwargs.get('file_folder')
        elif debug():
            stack = inspect.stack()
            self.file_folder = os.path.join(os.path.dirname(get_stack_frame(stack)[1]), 'Dump', date_folder, self.category)
        else:
            stack = inspect.stack()
            self.file_folder = os.path.join(os.path.expanduser('~'), 'Dump', os.path.basename(os.path.dirname(get_stack_frame(stack)[1])),
                         date_folder, self.category)

    def dump_page(self, page: str, file_prefix: str = '', file_name=None, **kwargs):
        if not os.path.exists(self.file_folder):
            os.makedirs(self.file_folder)
        if not file_name:
            file_name = self.get_file_name(file_prefix)
        file = os.path.join(self.file_folder, file_name)
        with open(file, 'w', encoding='utf-8') as fh:
            fh.write(page)
        return file

    def dump_dict(self, item: dict or list, file_prefix: str = '', file_name=None, **kwargs):
        if not os.path.exists(self.file_folder):
            os.makedirs(self.file_folder)
        if not file_name:
            file_name = self.get_file_name(file_prefix)
        file = os.path.join(self.file_folder, file_name)
        with open(file, 'w', encoding='utf-8') as fh:
            json.dump(item, fh)
        return file

    def dump_content(self, item, file_prefix: str = '', file_name=None, **kwargs):
        if not os.path.exists(self.file_folder):
            os.makedirs(self.file_folder)
        if not file_name:
            file_name = self.get_file_name(file_prefix)
        file = os.path.join(self.file_folder, file_name)
        with open(file, 'wb') as fh:
            fh.write(item)
        return file

    @staticmethod
    def get_file_name(file_prefix=''):
        return '_'.join([file_prefix, str(int(time())), str(uuid4())]).strip('_')

    def tarfile(self, source_dir: str = None, output_file: str = None):
        if source_dir is None:
            source_dir = self.file_folder
        if output_file is None:
            output_file = os.path.join(source_dir.rstrip('/') + '.tar.gz')
        with tarfile.open(output_file, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        return output_file

    @staticmethod
    def untarfile(source_file: str, output_folder: str = None):
        if output_folder is None:
            output_folder = os.path.dirname(source_file)
        tar = tarfile.open(source_file)
        tar.extractall(output_folder)
        return output_folder
        # tar.close()

    @staticmethod
    def unzipfile(source_file: str, output_folder: str = None):
        if output_folder is None:
            output_folder = source_file.strip('.zip')
        import zipfile
        with zipfile.ZipFile(source_file, 'r') as zip_ref:
            zip_ref.extractall(output_folder)

        return output_folder


if __name__ == '__main__':
    t = DumperHelper()
    result = t.unzipfile(r"C:\Users\Administrator\test\2020-04-07.zip")
    print(result)

