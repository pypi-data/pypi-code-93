from path import Path
from fs.copy import copy_fs
from fs.zipfs import ZipFS
from fs.osfs import OSFS
import typing as t


# Tested it works
def walk(path: str, pattern: str):
    return Path(path).walk(pattern)


# Tested it works
def list_all(path: str):
    # clean up.
    return Path(path).listdir()


# Tested ,It works
def find(path: str, pattern: str, **kwd):
    return Path(path).listdir(pattern)


# Tested it works
def create(path: str, **kwd):
    # Considering when dir not exist
    return Path(path).touch()


# Tested it works(Almost perfect)
def smart_delete(path: str):
    p = Path(path)
    if p.isdir():
        p.rmtree()
    elif p.isfile():
        p.remove()


# Tested it works(But feel... a litte weird?)
def delete(path: str, **kwd):
    p = Path(path)
    if p.isdir():
        # must be an exist dir
        print(
            f"The '{p}' is a dir(folder), and will not be deleted, if you want to"
            " delete a folder try to use delete_folder"
        )
        return
    p.remove()


def rmdir(path: str):
    p = Path(path)
    p.rmtree_p()


def rmdir_all(f_list: t.List[Path]):
    for p in f_list:
        rmdir(p)


# Tested ,it works
def _delete_all(f_list: list):
    for f in f_list:
        smart_delete(f)


# Tested ,it works(first appear in lesson 13)
def zip(src: str, dst: str):
    src, dst = Path(src), Path(dst)
    ffs = copy_fs(OSFS(dst), ZipFS(src))

    return ffs


def _zip_all(f_list: t.List[Path]):
    for f in f_list:
        ...


def unzip(src: str, dst: str):
    src, dst = Path(src), Path(dst)
    ffs = copy_fs(ZipFS(src), OSFS(dst, create=True))
    return ffs


def _upzip_all(f_list: t.List[Path]):
    for f in f_list:
        unzip(f, f.stem)


# It works(Not done yet)
def rename(
    path: str, new_name: str = None, with_suffix: str = None, with_prefix: str = None
):
    if new_name:
        if with_suffix or with_prefix:
            raise ValueError(
                "You don't need to do that, considering this"
                " way: 'prefix-newname.suffix'"
            )
        suffix = Path(path).ext
        _new_name = Path(path).dirname() / new_name + suffix
    elif with_suffix and with_prefix:
        # if new_name exists... wow...
        _new_name = Path(path).dirname() / with_prefix + Path(path).stem + with_suffix
    elif with_suffix:
        if new_name:
            raise ValueError("You can just pass 'newname.suffix' to new_name ")
        _new_name = Path(path).with_suffix(with_suffix)
    elif with_prefix:
        if new_name:
            raise ValueError("You can just pass 'prefix-newname.suffix' to new_name ")
        _new_name = Path(path).dirname() / with_prefix + Path(path).name

    else:
        raise ValueError("Need to pass at least one argument")

    Path(path).rename(_new_name)


def _rename_all(f_list: t.List[Path], with_prefix: str = None, with_suffix: str = None):

    if not with_prefix and not with_prefix:
        raise ValueError("To change files name, Must have a prefix or suffix ")

    for f in f_list:
        rename(f, with_suffix=with_suffix, with_prefix=with_prefix)


def create_folder(path: str, **kwd):
    p = Path(path)
    p.mkdir()


# Fixed, then test it.
def move(src: str, dst: str):
    p = Path(src)
    p.move(dst)


def _move_all(f_list: t.List[Path], dst: str):
    for f in f_list:
        f.move(dst)
