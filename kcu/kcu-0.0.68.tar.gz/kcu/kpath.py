from typing import List, Tuple, Optional, Union
import tempfile, platform, os, uuid


# allowed_extensions is an array, like ['jpg', 'jpeg', 'png']
def file_paths_from_folder(
    root_folder_path: str,
    allowed_extensions: Optional[List[str]] = None,
    ignored_extensions: Optional[List[str]] = ['.ds_store'],
    depth: int = -1,
    recursive: bool = True, #kept for convenience
) -> List[str]:
    """
        depth (int, optional): How far to check in folders. -1 means recursive, all the way down. Defaults to -1 (recursive).
        recursive (bool, optional): If True, sets depth to -1. Kept for convenience. Defaults to True.
    """
    root_folder_path = os.path.abspath(os.path.normpath(root_folder_path))
    file_paths = []
    current_depth = 0

    if allowed_extensions:
        allowed_extensions = [ae.lower() for ae in allowed_extensions]

    if ignored_extensions:
        ignored_extensions = [ie.lower() for ie in ignored_extensions]

    if recursive:
        depth = -1
    elif depth <= 0 and depth != -1:
        depth = 1

    def get_paths(src_folder_paths: List[str]) -> Tuple[List[str], List[str]]:
        _folder_paths = []
        _file_paths = []

        for src_folder_path in src_folder_paths:
            for (_, dir_names, file_names) in os.walk(src_folder_path):
                _folder_paths.extend([os.path.join(src_folder_path, dir_name) for dir_name in dir_names])

                for file_name in file_names:
                    should_add = True
                    lower_file_name = file_name.lower()

                    if allowed_extensions:
                        should_add = False

                        for allowed_extension in allowed_extensions:
                            if lower_file_name.endswith(allowed_extension):
                                should_add = True

                                break

                    if not should_add:
                        continue

                    if ignored_extensions:
                        for ignored_extension in ignored_extensions:
                            if lower_file_name.endswith(ignored_extension):
                                should_add = False

                                break

                    if should_add:
                        _file_paths.append(os.path.join(src_folder_path, file_name))

                break

        return _folder_paths, _file_paths

    recent_folder_paths = [root_folder_path]

    while current_depth < depth or depth == -1:
        current_depth += 1
        recent_folder_paths, new_file_paths = get_paths(recent_folder_paths)
        file_paths.extend(new_file_paths)

        if len(recent_folder_paths) == 0:
            return file_paths

    return file_paths

def folder_paths_from_folder(
    root_folder_path: str,
    depth: int = -1
) -> List[str]:
    """
        depth (int, optional): How far to check in folders. -1 means recursive, all the way down. Defaults to -1 (recursive).
    """
    root_folder_path = os.path.abspath(root_folder_path)
    folder_paths = []
    current_depth = 0

    if depth <= 0 and depth != -1:
        depth = 1

    def get_folder_paths(src_folder_paths: List[str]) -> List[str]:
        _folder_paths = []

        for src_folder_path in src_folder_paths:
            for (_, dir_names, _) in os.walk(src_folder_path):
                _folder_paths.extend([os.path.join(src_folder_path, dir_name) for dir_name in dir_names])

                break

        return _folder_paths

    recent_folder_paths = [root_folder_path]

    while current_depth < depth or depth == -1:
        current_depth += 1
        recent_folder_paths = get_folder_paths(recent_folder_paths)

        if len(recent_folder_paths) == 0:
            return folder_paths

        folder_paths.extend(recent_folder_paths)

    return folder_paths

def path_of_file(f: str) -> str:
    return os.path.abspath(f)

# If left None, the file path of the caller will be used, but in that case, the return value can be None too
def folder_path_of_file(file: Optional[str] = None) -> Optional[str]:
    if file is None:
        try:
            import inspect

            file = inspect.stack()[1][1]
        except:
            return None

    return os.path.dirname(path_of_file(file))

def path_for_subpath_in_current_folder(subpath: str) -> Optional[str]:
    try:
        import inspect

        return os.path.join(os.path.dirname(path_of_file(inspect.stack()[1][1])), subpath)
    except:
        return None

def temp_path_for_path(_path: str) -> str:
    import random, string

    folder_path = folder_path_of_file(_path)
    ext = extension(_path, include_dot=True)

    while True:
        proposed_path = os.path.join(
            folder_path,
            '.' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + ext
        )

        if not os.path.exists(proposed_path):
            return proposed_path

def new_tempdir(
    path_src: Optional[str] = None,
    appending_subpath: Optional[Union[str, List[str]]] = None,
    append_random_subfolder_path: bool = True,
    use_system_tmp_folder_for_macos: bool = False,
    create_folder_if_not_exists: bool = False
)-> str:
    if not path_src:
        path_src = '/tmp' if platform.system() == 'Darwin' and use_system_tmp_folder_for_macos else tempfile.gettempdir()

    if os.path.isfile(path_src):
        path_src = folder_path_of_file(path_src)

    if appending_subpath:
        if type(appending_subpath) == list:
            appending_subpath = os.path.sep.join(appending_subpath)

        path_src = os.path.join(path_src, appending_subpath)

    if append_random_subfolder_path:
        while True:
            path_src = os.path.join(path_src, 'temp-'+str(uuid.uuid4()))

            if not os.path.exists(path_src):
                break

    if create_folder_if_not_exists and not os.path.exists(path_src):
        os.makedirs(path_src)

    return path_src

def file_name(_path: str, include_extension: bool = True) -> str:
    basename = os.path.basename(_path)

    if not include_extension:
        basename = remove_extensions(basename)

    return basename

def extension(_path: str, include_dot: bool = False) -> Optional[str]:
    path_comps = _path.replace('/.', '/').split(".")

    if len(path_comps) == 1:
        return None

    ext = path_comps[-1]

    if include_dot:
        ext = '.' + ext

    return ext

def replace_extension(_path: str, new_extension: str) -> str:
    if not new_extension.startswith('.'):
        new_extension = '.' + new_extension

    return _path.replace(extension(_path, include_dot=True), new_extension)

def remove_extensions(_path: str) -> str:
    while True:
        ext = extension(_path, include_dot=True)

        if ext is None:
            return _path

        _path = _path.rstrip(ext)

def remove(_path: str) -> bool:
    if not os.path.exists(_path):
        return False

    try:
        if os.path.isdir(_path):
            import shutil

            shutil.rmtree(_path)
        else:
            os.remove(_path)
    except:
        return False

    return True