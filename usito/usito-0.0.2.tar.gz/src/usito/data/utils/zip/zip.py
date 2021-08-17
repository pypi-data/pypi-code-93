import shutil
import gzip
from pathlib import Path

from . import utils

def zip(source, destination = None):
    """
    Compresses the content of the source folder into a '.zip' file.

    Parameters
    ----------
    source : str
        Absolute or relative path of source folder.
    destination : str, optional
        Absolute or relative path of destination folder. If no path is 
        specified, the compressed file is stored on the same level as the 
        source folder. The default is None.

    Returns
    -------
    None.

    """
    source = utils._str_to_path(source)
    filename = source.parts[-1]
    destination = Path(destination)
    utils._zip_dir(source)
    shutil.make_archive(source, 'zip', source)
    if destination:
        if utils._destination_difference(source, destination):
            destination.mkdir(parents = True, exist_ok = True)
            shutil.move(str(source) + '.zip', 
                        str(destination) + f'\\{filename}.zip')
        
def targz(source, destination = None):
    """
    Compresses the content of the source folder into a '.tar.gz' file. This 
    format combines '.tar' archieving and '.gz' compression.

    Parameters
    ----------
    source : str
        Absolute or relative path of source folder.
    destination : str, optional
        Absolute or relative path of destination folder. If no path is 
        specified, the compressed file is stored on the same level as the 
        source folder. The default is None.

    Returns
    -------
    None.

    """
    source = utils._str_to_path(source)
    filename = source.parts[-1]
    utils._zip_dir(source)
    destination = Path(destination)
    shutil.make_archive(source, 'gztar', source)
    if destination:
        if utils._destination_difference(source, destination):
            destination.mkdir(parents = True, exist_ok = True)
            shutil.move(str(source) + '.tar.gz', 
                        str(destination) + f'\\{filename}.tar.gz')

def tar(source, destination = None):
    """
    Compresses the content of the source folder into a '.tar' file.

    Parameters
    ----------
    source : str
        Absolute or relative path of source folder.
    destination : str, optional
        Absolute or relative path of destination folder. If no path is 
        specified, the compressed file is stored on the same level as the 
        source folder. The default is None.

    Returns
    -------
    None.

    """
    source = utils._str_to_path(source)
    filename = source.parts[-1]
    utils._zip_dir(source)
    destination = Path(destination)
    shutil.make_archive(source, 'tar', source)
    if destination:
        if utils._destination_difference(source, destination):
            destination.mkdir(parents = True, exist_ok = True)
            shutil.move(str(source) + '.tar',
                        str(destination) + f'\\{filename}.tar')

def gz(source, destination = None):
    """
    Compresses the content of the source file into a '.gz' file.

    Parameters
    ----------
    source : str
        Absolute or relative path of source file.
    destination : str, optional
        Absolute or relative path of destination file without extension. If no 
        path is specified, the compressed file is stored on the same level as 
        the source file. The default is None.

    Returns
    -------
    None.

    """
    source = utils._str_to_path(source)
    filename, extension = source.stem, source.suffix
    utils._zip_file(source)
    with open(source, 'rb') as f_in:
        if not destination:
            destination = source + '.gz'
        else:
            destination = utils._str_to_path(destination)
            if destination.suffix == '':
                if not destination.is_dir():
                    destination.mkdir(parents = True, exist_ok = True)
                destination = str(destination) + f'\\{filename}{extension}.gz'
            else:
                if destination.suffix == extension:
                    destination = str(destination) + '.gz'
                elif destination.suffix == '.gz':
                    pass
                else:
                    raise TypeError("Specified destination path "
                                    f"'{destination}' not interpretable.")
                
        with gzip.open(destination, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
