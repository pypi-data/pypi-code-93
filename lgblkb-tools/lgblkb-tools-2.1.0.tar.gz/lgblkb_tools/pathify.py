import functools
import glob
import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path, PosixPath
from typing import Callable

from box import Box
from checksumdir import dirhash

from . import logger

get_name = lambda some_path: os.path.splitext(os.path.basename(some_path))[0]


def get_parent_dir(some_path, depth=1):
    for i in range(depth):
        some_path = os.path.dirname(os.path.abspath(some_path))
    return some_path


def create_path(*paths, stop_depth=0):
    path = os.path.join(*paths)
    os.makedirs(get_parent_dir(path, stop_depth), exist_ok=True)
    return path


def get_existing_path(paths, safe=False):
    for p in paths:
        if os.path.exists(p): return p
    if not safe:
        raise FileNotFoundError('Could not find any existing path.')


def get_splitted(path):
    folders = []
    while 1:
        path, folder = os.path.split(path)

        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)
            break
    folders.reverse()
    return folders


def create_zipfile(dir_to_zip, savepath=''):
    """Create a zip file from all the files under 'dir_to_zip'.

    The output zip file will be saved to savepath.
    If savepath ends with '.zip', then the output zip file will be
    saved AS 'savepath'. Necessary tree subdirectories are created automatically.
    Else, savepath is assumed to be a directory path,
    hence the output zip file will be saved TO 'savepath'
    directory. Necessary tree subdirectories are created automatically.

    :return absolute savepath
    """
    save_cwd = os.getcwd()
    dir_to_zip = os.path.abspath(dir_to_zip)
    if dir_to_zip in os.path.split(savepath)[0]: raise ValueError(
        'To avoid recursion), resultant "savepath" should not be located inside "dir_to_zip"',
        dict(dir_to_zip=dir_to_zip, savepath=savepath))
    parent_dir, dir_name = os.path.split(dir_to_zip)
    os.chdir(parent_dir)
    if savepath:
        if savepath.endswith('.zip'):
            create_path(savepath, stop_depth=1)
        else:
            create_path(savepath, stop_depth=0)
            savepath = os.path.join(savepath, dir_name + '.zip')
    else:
        savepath = dir_to_zip + '.zip'

    pwd_length = len(os.getcwd())
    with zipfile.ZipFile(savepath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(dir_to_zip):
            for name in sorted(dirnames):
                path = os.path.normpath(os.path.join(dirpath, name))
                zf.write(path, path[pwd_length + 1:])

            for name in filenames:
                path = os.path.normpath(os.path.join(dirpath, name))
                if os.path.isfile(path):
                    zf.write(path, path[pwd_length + 1:])

    os.chdir(save_cwd)
    return os.path.abspath(savepath)


def generate_name_portions(*args, __kv_delim__='-', **kwargs):
    arg_parts = [str(x) for x in args]
    kwarg_parts = [f"{k}{__kv_delim__}{v}" for k, v in kwargs.items() if v is not None]
    return arg_parts + kwarg_parts


def _get_name_parts_from_depth(path, include_depth):
    if type(include_depth) is Callable:
        parent_parts = include_depth(get_splitted(path))
    elif type(include_depth) is int:
        parent_parts = get_splitted(path)[-include_depth:]
    elif type(include_depth) in [tuple, list]:
        parent_parts = [get_splitted(path)[-x] for x in include_depth]
    elif type(include_depth) is slice:
        parent_parts = get_splitted(path)[-include_depth]
    else:
        raise ValueError(f'include_depth={include_depth}')
    return parent_parts


class Folder(os.PathLike):

    def __init__(self, path='', reactive=True, assert_exists=False):
        if isinstance(path, PosixPath):
            path = str(path)
        path = os.path.abspath(os.path.normpath(path))
        if self._is_file(path): path = get_parent_dir(path)
        if not self._exists(path):
            # possible_extension=os.path.splitext(path)[-1]
            # if possible_extension:
            # 	logger.warning('Provided folder path (which does not exist) appears to have an extension %s',possible_extension)
            # 	pass
            if assert_exists:
                raise AssertionError('Path should already exist.', dict(path=path))
            elif reactive:
                create_path(path)

        self.path = path
        self._class = functools.partial(self.__class__)
        self._inherit_class = self._class
        self.reactive = reactive

    def r(self):
        self.reactive = True
        return self

    def nr(self):
        self.reactive = False
        return self

    @property
    def name(self) -> str:
        return os.path.split(self.path)[-1]

    def __str__(self):
        # return f"{self.__class__.__name__}(r'{self.path}')"
        return self.path

    def get_filepath(self, *name_args, ext='', delim='_', include_depth=None, datetime_loc_index=None, iterated=False,
                     **name_kwargs):
        parts = list()
        if include_depth: parts.extend(_get_name_parts_from_depth(self.path, include_depth))
        parts.extend(generate_name_portions(*name_args, **name_kwargs))
        if datetime_loc_index is not None:
            if datetime_loc_index < 0: datetime_loc_index = len(parts) + datetime_loc_index + 1
            parts.insert(datetime_loc_index, datetime.now().strftime("%Y%m%d_%H%M%S"))

        assert parts, 'Nothing is provided to create filepath.'

        # output_path = os.path.join(self.path, delim.join(map(str, parts)).replace(' ', delim) + ext)
        output_path = os.path.join(self.path, delim.join(map(str, parts)) + ext)
        if iterated:
            return create_iterated_path(output_path)
        else:
            return output_path

    def _exists(self, path):
        return os.path.exists(path)

    def _is_file(self, path):
        return os.path.isfile(path)

    def _create_dir(self, dirpath, **kwargs):
        return self._inherit_class(dirpath, **kwargs)

    def create(self, *name_args, delim='_', datetime_loc_index=None, iterated=False, reactive=None, **name_kwargs):
        """
        :param name_args: args that are converted to name portions.
        :param delim: delimiter to use between the name string portions
        :param datetime_loc_index: index location of datetime in the resultant list of name portions.
        :param iterated: if iterated==True, method it will first check for existence of the folder. If exists, it creates a folder with new name,
        which is generated by incrementing the folder name.
        :param reactive: if not provided, default value is used. If provided, new folder will be created with specified value.
        :param name_kwargs: kwargs that are converted to name portions.
        :return: new instance of the class.
        :rtype: Folder
        """
        new_dirpath = self.get_filepath(*name_args, ext='', delim=delim, include_depth=None,
                                        datetime_loc_index=datetime_loc_index, iterated=iterated, **name_kwargs)
        # new_folder=self._create_dir(new_dirpath,**({} if reactive is None else dict(reactive=reactive)))
        new_folder = self._create_dir(new_dirpath, **dict(reactive=self.reactive if reactive is None else reactive))
        return new_folder

    def delete(self):
        # assert self.reactive,f'Folder {self.path} is not reactive'
        shutil.rmtree(self.path, ignore_errors=True)

    @logger.trace(skimpy=True)
    def clear(self):
        # assert self.reactive,f'Folder {self.path} is not reactive'
        self.delete()
        # try:
        #
        # except FileNotFoundError:
        # 	# lu.simple_logger.warning('FileNotFoundError when trying to clear up the results folder. Passing on.')
        # 	pass
        create_path(self.path)
        return self

    @classmethod
    def mkdtemp(cls, suffix=None, prefix=None, dir=None):
        return cls(tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir))

    def glob_delete(self, *patterns, recursive=True):
        glob_search_results = self.glob_search(*patterns, recursive=recursive)
        for glob_search_result in glob_search_results:
            if os.path.isdir(glob_search_result):
                shutil.rmtree(glob_search_result)
            else:
                os.remove(glob_search_result)
        return self

    @property
    def children(self):
        return self.glob_search('*')

    def glob_search(self, *patterns, recursive=True):
        return glob.glob(self.get_filepath(*patterns), recursive=recursive)

    @logger.trace(skimpy=True)
    def zip(self, zip_filepath='', forced=False):
        zip_filepath = zip_filepath or self.parent().get_filepath(self.name, ext='.zip')
        if len(get_splitted(zip_filepath)) == 1: zip_filepath = self.parent().get_filepath(zip_filepath)
        if not zip_filepath.endswith('.zip'): zip_filepath += '.zip'
        # if not self.reactive: return zip_filepath

        # assert self.reactive,f'Folder {self.path} is not reactive'

        if os.path.exists(zip_filepath):
            if forced:
                os.remove(zip_filepath)
            else:
                return zip_filepath

        create_zipfile(self.path, zip_filepath)
        return zip_filepath

    @logger.trace(skimpy=True)
    def unzip(self, zip_filepath, create_subdir=True):
        # assert self.reactive,f'Folder {self.path} is not reactive'
        # if save_path_formatter is None: save_path_formatter=lambda x:x
        # zip_path=[zip_filepath,
        #           zip_filepath+'.zip',
        #           self.get_filepath(zip_filepath),
        #           self.get_filepath(zip_filepath,ext='.zip')]
        # zip_path=get_existing_path(zip_path)
        # assert not os.path.isdir(zip_path),f'The folder "{zip_filepath}" cannot be unzipped.'
        if create_subdir:
            zipfilename = os.path.splitext(Path(zip_filepath).name)[0]
            # logger.debug('zipfilename: %s',zipfilename)
            dst_folder_path = self.create(zipfilename).path
        # logger.debug('dst_folder_path: %s',dst_folder_path)
        else:
            dst_folder_path = self.path
        if not self.reactive: return self._inherit_class(dst_folder_path)
        shutil.unpack_archive(zip_filepath, dst_folder_path, 'zip')
        return self._inherit_class(dst_folder_path)

    @logger.trace(skimpy=True)
    def rename(self, new_name):
        new_path = self.parent().get_filepath(new_name)
        # new_path=os.path.join(get_parent_dir(self.path),new_name)
        if self.reactive: os.rename(self.path, new_path)
        self.path = new_path
        return self

    @logger.trace(skimpy=True)
    def move_to(self, dst_path):
        if not isinstance(dst_path, str): dst_path = dst_path.path
        # if self.reactive: shutil.move(self.path,dst_path)
        shutil.move(self.path, dst_path)
        self.path = os.path.join(dst_path, self.name)
        return self

    def parent(self, depth=1):
        """

        :rtype: Folder
        """
        return self._inherit_class(get_parent_dir(self.path, depth=depth))

    @logger.trace(skimpy=True)
    def copy_to(self, dst_folder, new_name='', forced=False):
        """

        :rtype: Folder
        """
        new_name = new_name or self.name
        dst_folder_path = self._inherit_class(dst_folder).get_filepath(new_name)

        delete_dst = lambda: shutil.rmtree(dst_folder_path, ignore_errors=True)
        resulter = lambda: self._class(dst_folder_path)

        if os.path.exists(dst_folder_path):
            if forced:
                delete_dst()
            else:
                source_hashsum = dirhash(self.path)
                destination_hashsum = dirhash(dst_folder_path)
                if source_hashsum == destination_hashsum:
                    return resulter()
                else:
                    delete_dst()

        shutil.copytree(self.path, dst_folder_path)
        return resulter()

    def size(self, byte_factor=1e-9):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size * byte_factor

    @property
    def exists(self):
        return self._exists(self.path)

    def assert_exists(self):
        assert self.exists
        return self

    # def create_iterated(self,start=None,delim='_',empty_ok=False):
    # 	if empty_ok:
    # 		validator_func=lambda existing_path:not self._inherit_class(existing_path).children
    # 	else:
    # 		validator_func=lambda existing_path:existing_path==self.path
    #
    # 	new_iter_folder_path=create_iterated_path(self.path,start,delim,validator_func=validator_func)
    # 	last_part=new_iter_folder_path.split(delim)[-1]
    # 	if last_part.isnumeric() and int(last_part)==(start or 0):
    # 		new_folder=self.rename(new_iter_folder_path)
    # 	else:
    # 		new_folder=self.__class__(new_iter_folder_path)
    # 		if not new_folder==self and not self.children(): self.delete()
    # 	return new_folder

    def __getitem__(self, item):
        item = str(item)
        if os.path.splitext(item)[-1]:
            return self.get_filepath(item)
        else:
            return self.create(item)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.path == other
        else:
            return self.path == other.path

    def __setitem__(self, key, value):
        filename, ext = os.path.splitext(key)
        if isinstance(value, str):
            string_obj = value
        elif type(value) in [list, tuple]:
            string_obj = '\n'.join(map(str, value))
        elif isinstance(value, dict):
            ext = ext or '.yaml'
            if ext in ['.yaml', '.yml']:
                Box(value).to_yaml(filename=self.get_filepath(filename, ext=ext))
                return
            elif ext == '.json':
                Box(value).to_json(filename=self.get_filepath(filename, ext=ext))
                return
            else:
                string_obj = '\n'.join(map(lambda kv: f"{kv[0]}: {kv[1]}", value.items()))

        else:
            string_obj = str(value)
        # def writer(filehandler):
        # 	for k,v in value.items():
        # 		filehandler.writelines([f"{k}: {v}"])

        with open(self.get_filepath(filename, ext=ext or '.txt'), 'w') as fh:
            fh.write(str(string_obj))

    def __repr__(self):
        return f"{self.__class__.__name__}(r'{self.path}')"

    def __fspath__(self):
        return self.path


def create_iterated_path(iterated_path: str, start=None, delim='_', validator_func=None) -> str:
    if validator_func is None: validator_func = lambda x: False
    base_path, item_name_with_ext = os.path.split(iterated_path)
    item_name, ext = os.path.splitext(item_name_with_ext)

    curr_iter = 0 if start is None else start
    while True:
        new_item_name = delim.join([item_name, f'{curr_iter}'])
        new_itempath = os.path.join(base_path, new_item_name + ext)
        if not os.path.exists(new_itempath) or validator_func(new_itempath): return new_itempath
        curr_iter += 1
