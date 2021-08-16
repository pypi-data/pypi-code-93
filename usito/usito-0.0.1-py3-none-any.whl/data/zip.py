from pathlib import Path
from .utils.zip import zip # provides all zipping functions
from .utils.zip import unzip # provides all unzipping functions

_ZIP_MAP = {'zip': zip.zip,
            'targz': zip.targz,
            'tar': zip.tar,
            'gz': zip.gz
            }

_UNZIP_MAP = {'zip': unzip.zip,
              'targz': unzip.targz,
              'tar': unzip.tar,
              'gz': unzip.gz
              }

class FileZipper:
    def __init__(self, source, destination = None):
        """
        Base class for all zippers, specifying their functionality.

        Parameters
        ----------
        source : str or Path object
            Source path.
        destination : str or Path object, optional
            Destination path. The default is None.

        Returns
        -------
        None.

        """
        path = Path(source)
        self.source = path
        if destination is None:
            destination = str(path.parents[0])
        self.destination = Path(destination)

    def _zipper_selector(self, file_type):
        """
        Selector method that chooses the correct zipper function depending on
        the defined 'file_type'.

        Parameters
        ----------
        file_type : str
            Zipper format. Possible options can be seen using the method 
            'get_zip_map()'.

        Raises
        ------
        NoZipperError
            Raises error if 'file_type' is not included in zip map.

        Returns
        -------
        None.

        """
        path = Path(self.source)
        
        if file_type is None:
            file_type = path.suffix
        
        if file_type not in _ZIP_MAP.keys():
            raise NoZipperError(f"The requested file type {file_type} cannot "
                                "be interpreted or is not implemented yet. "
                                "Try a different file type.")
        else:
            _ZIP_MAP[file_type](path, self.destination)
            print(f"Compressed '{path.name}' and the compressed file is "
                  f"stored at '{self.destination}'.")
            
    def _unzipper_selector(self, file_type):
        """
        Selector method that chooses the correct unzipper function depending 
        on the defined 'file_type'.

        Parameters
        ----------
        file_type : str
            Zipper format. Possible options can be seen using the method 
            'get_unzip_map()'.

        Raises
        ------
        NoZipperError
            Raises error if 'file_type' is not included in unzip map.

        Returns
        -------
        None.

        """
        path = Path(self.source)
        
        if file_type is None:
            file_type = path.suffix
        
        if file_type not in _UNZIP_MAP.keys():
            raise NoZipperError(f"The requested file type {file_type} cannot "
                                "be interpreted or is not implemented yet. "
                                "Try a different file type.")
        else:
            _UNZIP_MAP[file_type](path, self.destination)
            print(f"Unzipped '{path.name}' and the restored files are "
                  f"stored at '{self.destination}'.")
            
    def get_zip_map(self):
        """
        Lists all possible file formats for the compression.

        Returns
        -------
        Zip map with all possible formats for zipping.

        """
        zip_map = _ZIP_MAP.keys()
        return zip_map
    
    def get_unzip_map(self):
        """
        Lists all possible file formats for the unzipping.

        Returns
        -------
        Zip map with all possible formats for unzipping.

        """
        unzip_map = _UNZIP_MAP.keys()
        return unzip_map
               
class Zip(FileZipper):
    def __init__(self, source, destination):
        """
        Base class for all zippers, specifying their functionality.

        Parameters
        ----------
        source : str or Path object
            Source path.
        destination : str or Path object, optional
            Destination path. The default is None.

        Returns
        -------
        None.

        """
        super().__init__(source, destination)
    
    def zip(self):
        _ZIP_MAP['zip'](self.source, self.destination)
    
    def tar(self):
        _ZIP_MAP['tar'](self.source, self.destination)
    
    def targz(self):
        _ZIP_MAP['targz'](self.source, self.destination)
    
    def gz(self):
        _ZIP_MAP['gz'](self.source, self.destination)
        
class Unzip(FileZipper):
    """
    Base class for all unzippers, specifying their functionality.

    Parameters
    ----------
    source : str or Path object
        Source path.
    destination : str or Path object, optional
        Destination path. The default is None.

    Returns
    -------
    None.

    """
    def __init__(self, source, destination):
        super().__init__(source, destination)
    
    def zip(self):
        _UNZIP_MAP['zip'](self.source, self.destination)
    
    def tar(self):
        _UNZIP_MAP['tar'](self.source, self.destination)
    
    def targz(self):
        _UNZIP_MAP['targz'](self.source, self.destination)
    
    def gz(self):
        _UNZIP_MAP['gz'](self.source, self.destination)

class NoZipperError(Exception):
    """
    Error specific to the load module: Raised if no zipper is assigned.
    
    """
    pass    

def zip(source, destination = None, file_type = 'zip'):
    """
    Zipping function that replaces the 'Zip' class. All functionality can also
    be called by using this function.

    Parameters
    ----------
    source : str or Path object
        Source path.
    destination : str or Path object, optional
        Destination path. The default is None.
    file_type : str, optional
        Defines the file format. The default is 'zip'.

    Returns
    -------
    None.

    """
    file = FileZipper(source, destination)
    file._zipper_selector(file_type)

def unzip(source, destination = None, file_type = "zip"):
    """
    Unzipping function that replaces the 'Unzip' class. All functionality can 
    also be called by using this function.

    Parameters
    ----------
    source : str or Path object
        Source path.
    destination : str or Path object, optional
        Destination path. The default is None.
    file_type : str, optional
        Defines the file format. The default is 'zip'.

    Returns
    -------
    None.

    """
    file = FileZipper(source, destination)
    file._unzipper_selector(file_type)

def get_zip_map():
    """
    Lists all possible file formats for the compression.

    Returns
    -------
    Zip map with all possible formats for zipping.

    """
    zip_map = _ZIP_MAP.keys()
    return zip_map

def get_unzip_map():
    """
    Lists all possible file formats for the unzipping.

    Returns
    -------
    Zip map with all possible formats for unzipping.

    """
    unzip_map = _UNZIP_MAP.keys()
    return unzip_map

