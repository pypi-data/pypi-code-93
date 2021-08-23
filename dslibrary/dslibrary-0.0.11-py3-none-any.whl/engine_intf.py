"""
Interfaces to remote engines, i.e. filesystems, SQL & NoSQL databases, etc..
"""
import pathlib
import typing


class FileSystem(object):
    """
    A very much simplified version of fsspec.AbstractFileSystem
    """
    def mkdir(self, path, create_parents=True, **kwargs):
        pass

    def rmdir(self, path):
        pass  # not necessary to implement, may not have directories

    def ls(self, path, detail=True, **kwargs):
        '''
        - full path to the entry (without protocol)
        - size of the entry, in bytes. If the value cannot be determined, will
          be ``None``.
        - type of entry, "file", "directory" or other
        '''
        pass

    def stat(self, path, **kwargs):
        # dict with keys: name (full path in the FS), size (in bytes), type (file,
        # directory, or something else) and other FS-specific keys.
        pass

    def exists(self, path, **kwargs):
        """Is there a file at the given path"""
        try:
            self.stat(path, **kwargs)
            return True
        except FileNotFoundError:
            return False

    def rm(self, path, recursive=False, maxdepth=None):
        pass

    def open(self, path, mode="rb", block_size=None, cache_options=None, **kwargs):
        pass


class WriteNotAllowed(Exception):
    pass


class FileSystemLocal(FileSystem):
    """
    A chroot'ed set of local files.
    """
    def __init__(self, root: str):
        self.root = pathlib.Path(root)

    def _loc(self, path: str):
        out = self.root / path.strip("/")
        if ".." in out.parts:
            raise ValueError(".. not allowed")
        return out

    def mkdir(self, path, create_parents=True, **kwargs):
        self._loc(path).mkdir(parents=create_parents, mode=kwargs.get('mode'))

    def rmdir(self, path):
        self._loc(path).rmdir()

    def ls(self, path=".", detail=True, **kwargs):
        out = []
        for f in self._loc(path).glob("*"):
            out.append(self._file_info(f))
        return out

    @staticmethod
    def _file_info(f):
        return {
            "name": f.name,
            "size": f.stat().st_size,
            "type": "directory" if f.is_dir() else "symlink" if f.is_symlink() else "file"
        }

    def stat(self, path, **kwargs):
        return self._file_info(self._loc(path))

    def rm(self, path, recursive=False, maxdepth=None):
        # TODO support recursive directory removal
        self._loc(path).unlink(missing_ok=True)

    def open(self, path, mode="rb", **kwargs):
        return self._loc(path).open(mode=mode)


class FileSystemReadOnly(FileSystem):
    """
    Block write access.
    """
    def __init__(self, target: FileSystem):
        self._target = target

    def mkdir(self, path, create_parents=True, **kwargs):
        raise WriteNotAllowed()

    def rmdir(self, path):
        raise WriteNotAllowed()

    def ls(self, *args, **kwargs):
        return self._target.ls(*args, **kwargs)

    def stat(self, *args, **kwargs):
        return self._target.stat(*args, **kwargs)

    def rm(self, path, recursive=False, maxdepth=None):
        raise WriteNotAllowed()

    def open(self, path, mode="rb", **kwargs):
        if "w" in mode or "a" in mode:
            raise WriteNotAllowed()
        return self._target.open(path, mode=mode, **kwargs)


class SqlDatabase(object):
    """
    The methods expected of a database connection.  These are the methods one usually expects to exist in the connection
    object returned by a DBI-compliant driver.
    """
    def cursor(self):
        """ return a cursor """
    def close(self):
        """ clean up """
    def commit(self):
        """ commit changes (placeholder) """
    def rollback(self):
        """ roll back changes (placeholder) """


class NoSqlDatabase(object):
    """
    The methods expected for a NoSQL database.
    """
    def query(self, collection: str, query: dict=None, limit: int=None, **kwargs) -> typing.Iterable[dict]:
        """
        Scan for documents, or retrieve a specific document.
        :param collection:   Name of collection.
        :param query:        JSON-style query with named fields to exactly match.  Follows an implementation-dependent
                             subset of the MongoDB conventions.  Example: {"x": {"$lt": 100}}
        :param limit:        Maximum number of records.
        :return:    An iteration of matched documents.
        """

    def insert(self, collection: str, doc: dict, **kwargs):
        """
        Add a document to a collection.  Note that some systems have restrictions on field names.  For instance,
        MongoDB does not allow fields to start with '$'.

        :returns:  ID of new row.
        """

    def update(self, collection: str, filter: dict, changes: dict, upsert: bool=False, **kwargs):
        """
        Update documents in a collection.

        :param collection:  Name of collection we're working on.
        :param filter:      Which documents to update.
        :param changes:     A {} with named changes to make.  An implementation-dependent subset of MongoDB conventions
                            will be supported.  For instance, {"$inc": {"x": 3}}.
        """

    def delete(self, collection: str, filter: dict, **kwargs):
        """
        Delete documents from a collection.

        :param collection:  Name of collection we're working on.
        :param filter:      Which documents to delete.
        """


class NoSQLReadOnly(NoSqlDatabase):
    """
    Block write access.
    """
    def __init__(self, target: NoSqlDatabase):
        self._target = target

    def query(self, *args, **kwargs):
        return self._target.query(*args, **kwargs)

    def insert(self, collection: str, doc: dict, **kwargs):
        raise WriteNotAllowed()

    def update(self, collection: str, filter: dict, changes: dict, upsert: bool=False, **kwargs):
        raise WriteNotAllowed()

    def delete(self, collection: str, filter: dict, **kwargs):
        raise WriteNotAllowed()
