import shutil
import gzip

from . import utils

def zip(source, destination = None):
    """
    Unpacks the content of the source '.zip' file.

    Parameters
    ----------
    source : str
        Absolute or relative path of source file including filename but 
        without extension.
    destination : str, optional
        Absolute or relative path of destination folder. If no path is 
        specified, the compressed file is stored on the same level as the 
        source file. The default is None.

    Returns
    -------
    None.

    """
    source = utils._str_to_path(source)
    destination = utils._get_destination(destination)
    utils._unzip_file(source)
    
    if not destination:
        destination = source.parents[0]
        shutil.unpack_archive(source, destination, 'zip')
    else:
        shutil.unpack_archive(source, destination, 'zip')
        
def targz(source, destination = None):
    """
    Unpacks the content of the source '.tar.gz' file.

    Parameters
    ----------
    source : str
        Absolute or relative path of source file including filename but 
        without extension.
    destination : str, optional
        Absolute or relative path of destination folder. If no path is 
        specified, the compressed file is stored on the same level as the 
        source file. The default is None.

    Returns
    -------
    None.

    """
    source = utils._str_to_path(source)
    destination = utils._get_destination(destination)
    utils._unzip_file(source)
    
    if not destination:
        destination = source.parents[0]
        shutil.unpack_archive(source, destination, 'gztar')
    else:
        shutil.unpack_archive(source, destination, 'gztar')

def tar(source, destination = None):
    """
    Unpacks the content of the source '.tar' file.

    Parameters
    ----------
    source : str
        Absolute or relative path of source file including filename but 
        without extension.
    destination : str, optional
        Absolute or relative path of destination folder. If no path is 
        specified, the compressed file is stored on the same level as the 
        source file. The default is None.

    Returns
    -------
    None.

    """
    source = utils._str_to_path(source)
    destination = utils._get_destination(destination)
    utils._unzip_file(source)
    
    if not destination:
        destination = source.parents[0]
        shutil.unpack_archive(source, destination, 'tar')
    else:
        shutil.unpack_archive(source, destination, 'tar')

def gz(source, destination = None):
    """
    Unpacks the content of the source '.gz' file.

    Parameters
    ----------
    source : str
        Absolute or relative path of source file including filename and 
        extension.
    destination : str, optional
        Absolute or relative path of destination file without extension. If no 
        path is specified, the unpacked file is stored on the same level as 
        the source file. The default is None.

    Returns
    -------
    None.

    """
    source = utils._str_to_path(source)
    filename, extension = source.stem, source.suffix
    destination = utils._get_destination(destination)
    utils._unzip_file(source)
    
    with gzip.open(source, 'rb') as f_in:
        if destination is None:
            destination = str(source) + f'\\{filename}{extension}'
        else:
            destination = str(destination) +  f'\\{filename}{extension}'
        with open(destination, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
