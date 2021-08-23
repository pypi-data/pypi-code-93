# -*- coding: utf-8 -*-
"""
Utilities to abstractly handle filesystem operations
"""
import inspect
from .filesystems import Local, S3


class FileSystem:
    """
    Class to abstract file location and allow file-system commands that are
    """
    def __init__(self, path, anon=False, profile=None, **kwargs):
        """
        Parameters
        ----------
        path : str
            S3 object path or file path
        anon : bool, optional
            Whether to use anonymous credentials, by default False
        profile : str, optional
            AWS credentials profile, by default None
        """
        self._path = path
        self._handler = None
        if path.lower().startswith('s3:'):
            self._fs = S3(path, anon=anon, profile=profile, **kwargs)
        else:
            self._fs = Local(path)

        self._check_operations()

    def __repr__(self):
        msg = ("{} operations on {}"
               .format(self.__class__.__name__, self.path))

        return msg

    def __enter__(self):
        self._handler = self.open()

        return self._handler

    def __exit__(self, type, value, traceback):
        try:
            self._handler.close()
        except AttributeError:
            pass
        except Exception:
            raise

        if type is not None:
            raise

    @property
    def path(self):
        """
        File path to perform filesystem operation on

        Returns
        -------
        str
        """
        return self._path

    def _check_operations(self):
        """
        Check to ensure the File System class being used has all of the
        required file system operations defined.
        """
        operations = [attr for attr, attr_obj
                      in inspect.getmembers(self.__class__)
                      if not attr.startswith('_')
                      and not isinstance(attr_obj, property)
                      and not inspect.ismethod(attr_obj)]

        missing = list(set(operations) - set(self._fs.operations))
        if missing:
            msg = ("The following filesystem operations are not defined in "
                   "{}:\n{}".format(missing, self._fs))
            raise NotImplementedError(msg)

        return operations

    def cp(self, dst, **kwargs):
        """
        Copy file to given destination

        Parameters
        ----------
        dst : str
            Destination path
        kwargs : dict
            kwargs for s3fs.S3FileSystem.copy
        """
        self._fs['cp'](self.path, dst, **kwargs)

    def exists(self):
        """
        Check if file path exists

        Returns
        -------
        bool
        """
        return self._fs['exists'](self.path)

    def isfile(self):
        """
        Check if path is a file

        Returns
        -------
        bool
        """
        return self._fs['isfile'](self.path)

    def isdir(self):
        """
        Check if path is a directory

        Returns
        -------
        bool
        """
        return self._fs['isdir'](self.path)

    def glob(self, **kwargs):
        """
        Find all file paths matching the given pattern

        Parameters
        ----------
        kwargs : dict
            kwargs for s3fs.S3FileSystem.glob

        Returns
        -------
        list
        """
        return self._fs['glob'](self.path, **kwargs)

    def ls(self):
        """
        List everyting under given path

        Returns
        -------
        list
        """
        return sorted(self._fs['ls'](self.path))

    def mkdirs(self, **kwargs):
        """
        Make desired directory and any intermediate directories

        Parameters
        ----------
        kwargs : dict
            kwargs for s3fs.S3FileSystem.mkdirs
        """
        self._fs['mkdirs'](self.path, **kwargs)

    def mv(self, dst, **kwargs):
        """
        Move file or all files in directory to given destination

        Parameters
        ----------
        dst : str
            Destination path
        kwargs : dict
            kwargs for s3fs.S3FileSystem.mv
        """
        self._fs['mv'](self.path, dst, **kwargs)

    def open(self, mode='rb', **kwargs):
        """
        Open S3 object and return a file-like object

        Parameters
        ----------
        mode : str
            Mode with which to open the s3 object
        kwargs : dict
            kwargs for s3fs.S3FileSystem.open

        Returns
        -------
        Return a file-like object from the filesystem
        """
        return self._fs['open'](self.path, mode=mode, **kwargs)

    def rm(self, **kwargs):
        """
        Delete file or files in given directory

        Parameters
        ----------
        kwargs : dict
            kwargs for s3fs.S3FileSystem.rm
        """
        self._fs['rm'](self.path, **kwargs)

    def size(self):
        """
        Get file size in bytes

        Returns
        -------
        float
        """
        return self._fs['size'](self.path)

    def walk(self):
        """
        Recursively search directory and all sub-directories

        Returns
        -------
        path : str
            Root path
        directory : list
            All directories in path
        file : list
            All files in path
        """
        return self._fs['walk'](self.path)

    @classmethod
    def copy(cls, src_path, dst_path, anon=False, profile=None, **kwargs):
        """
        Copy file(s) from src_path to dst_path. Either can be local or in the
        cloud.

        Parameters
        ----------
        src_path : str
            Source path to copy file(s) from, can be local or in the cloud
        dst_path : str
            Destination path to copy file(s) to, can be local or in the cloud
        anon : bool, optional
            Whether to use anonymous credentials, by default False
        profile : str, optional
            AWS credentials profile, by default None
        """
        s3 = (src_path.lower().startswith('s3:')
              or dst_path.lower().startswith('s3:'))
        if s3:
            path = 's3:'
        else:
            path = ''

        fs = cls(path, anon=anon, profile=profile, **kwargs)

        fs._fs['cp'](src_path, dst_path)
