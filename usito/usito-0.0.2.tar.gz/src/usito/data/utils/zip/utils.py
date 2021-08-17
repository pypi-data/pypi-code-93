from pathlib import Path

def _str_to_path(str_path):
    """
    Converts given string into a 'Path' object (pathlib).

    Parameters
    ----------
    str_path : str
        The string (or path respectively) that defines the 'Path' object.

    Returns
    -------
    path : Path object
        Converted 'Path' object.

    """
    if not isinstance(str_path, Path):
        path = Path(str_path)
    else:
        path = str_path
    return path

def _zip_dir(path):
    """
    Reviews whether path object is a folder or not.

    Parameters
    ----------
    path : Path object
        Path that is reviewed.

    Raises
    ------
    TypeError
        Raises error if 'Path' object is not a folder.

    Returns
    -------
    None.

    """
    if path.is_file():
        raise TypeError(f"Cannot compress the file at '{path}'. Only folders "
                        "are allowed.")

def _zip_file(path):
    """
    Reviews whether path object is a file or not.

    Parameters
    ----------
    path : Path object
        Path that is reviewed.

    Raises
    ------
    TypeError
        Raises error if 'Path' object is not a file.

    Returns
    -------
    None.

    """
    if path.is_dir():
        raise TypeError(f"Cannot compress the folder at '{path}'. Only files "
                        "are allowed.")
        
def _unzip_dir(path):
    """
    Reviews whether path object is a folder or not.

    Parameters
    ----------
    path : Path object
        Path that is reviewed.

    Raises
    ------
    TypeError
        Raises error if 'Path' object is not a folder.

    Returns
    -------
    None.

    """
    if path.is_file():
        raise TypeError(f"Cannot unzip the file at '{path}'. Only folders "
                        "are allowed.")

def _unzip_file(path):
    """
    Reviews whether path object is file or not.

    Parameters
    ----------
    path : Path object
        Path that is reviewed.

    Raises
    ------
    TypeError
        Raises error if 'Path' object is not a file.

    Returns
    -------
    None.

    """
    if path.is_dir():
        raise TypeError(f"Cannot unzip the folder at '{path}'. Only files "
                        "are allowed.")

def _destination_difference(source, destination):
    """
    Reviews whether source and destination path are the same.

    Parameters
    ----------
    source : Path object
        Source path that is reviewed.
        
    desination : Path object
        Destination path that is reviewed.

    Returns
    -------
    Boolean.

    """
    if destination == source.parents[0]:
        return False
    else:
        return True
    
def _get_destination(destination):
    """
    Same as _str_to_path() but with another return option: None, if no path is
    given.

    Parameters
    ----------
    destination : str or Path object
        Destination path that is reviewed.

    Returns
    -------
    Boolean.

    """
    if not destination:
        return None
    else:
        destination = Path(destination)
        return destination