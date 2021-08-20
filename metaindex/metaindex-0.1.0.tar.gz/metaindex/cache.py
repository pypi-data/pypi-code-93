import collections
import datetime
import pathlib
import sqlite3
import os
import logging
import re
import sys

import multidict

from metaindex import indexer
from metaindex import configuration
from metaindex import sql
from metaindex import stores
from metaindex import shared
from metaindex.query import Query


class Cache:
    CACHE_FILENAME = "index" + os.extsep + "db"

    TYPE_DATETIME = 'd'
    TYPE_INT = 'i'
    TYPE_FLOAT = 'f'
    TYPE_STR = None

    Entry = collections.namedtuple('Entry', ['path', 'mimetype', 'last_accessed'])

    def __init__(self, config=None):
        self.config = config or configuration.load()
        self.db = None

        self.collection_metadata = config.list('General', 'collection-metadata', '')
        self.collection_metadata = set(sum([[fn + store.SUFFIX for store in stores.STORES] for fn in self.collection_metadata], start=[]))
        self.recursive_extra_metadata = config.bool("General", "recursive-extra-metadata", "y")
        self.ignore_dirs = config.list('General', 'ignore-directories', "", separator="\n")
        self.ignore_tags = config.list('General', 'ignore-tags', "")

        self._open_db()

    def refresh(self, paths=None, recursive=True, processes=None):
        """(Re-)Index all items found in the given paths or all cached items if paths is None.

        If any item in the list is a directory and recursive is True, all
        items inside that directory (including any all subdirectories) will
        be indexed, too.

        processes may be set to a number of processes that will be used in
        parallel to index the files. If left at None, there will be as many
        processes launched as CPUs are available.
        """
        if paths is None:
            paths = [row['path'] for row in self.db.execute("select `path` from `files`")]

        elif isinstance(paths, (set, tuple)):
            paths = list(paths)

        elif not isinstance(paths, list):
            paths = [paths]

        if len(paths) == 0:
            return multidict.MultiDict()

        paths = [pathlib.Path(path).expanduser().resolve() for path in paths]

        # filter out ignored directories
        paths = [path for path in paths if not any([ignoredir in path.parts for ignoredir in self.ignore_dirs])]

        dirs = [path for path in paths if path.is_dir()]
        files = {path for path in paths if path.is_file() and not self.is_sidecar_file(path)}
        files |= {fn for fn in indexer.find_files(dirs, recursive) if not self.is_sidecar_file(fn)}

        # TODO: allow disabling of sidecar storage(s)
        # existing sidecar files per file to be indexed
        sidecar_files = self._find_sidecar_files(files)
        
        # existing collection sidecar files per folder
        collection_sidecar_files = self._find_collection_sidecar_files(files)
        # keep track of what collection sidecar files have been parsed already, so we can be lazy
        parsed_collection_sidecar_files = set()

        # files to process through indexing
        to_index = []
        # cache of last_modified dates for files
        last_modified = dict([(fn, shared.get_last_modified(fn)) for fn in sum(sidecar_files.values(), start=[])]
                           + [(fn, shared.get_last_modified(fn)) for fn in sum(collection_sidecar_files.values(), start=[])]
                           + [(fn, shared.get_last_modified(fn)) for fn in files])
        # cache of extra metadata values per file (absolute path)
        extra_metadata_cache = {}

        def match_collection_sidecar_files(fn):
            queue = [fn.parent]
            if self.recursive_extra_metadata:
                parent = fn.parent.parent
                # walk up the tree and add all directories into the queue
                while True:
                    queue.append(parent)
                    if parent == parent.parent:
                        break
                    parent = parent.parent
            return sum([collection_sidecar_files.get(path, []) for path in queue], start=[])

        to_ignore = set()

        # check what files have changed since the cache was created
        for file_ in files:
            if file_ in to_ignore:
                continue

            coll_sidecars = match_collection_sidecar_files(file_)
            relevant_files = [file_] + sidecar_files.get(file_, []) + coll_sidecars
            current_lm = max([last_modified[fn] for fn in relevant_files])

            query = "select `last_modified` from `files` where `path` = ?"
            row = self.db.execute(query, (str(file_), )).fetchone()

            if row is None:
                to_index.append(file_)
            else:
                cached_lm = sql.str_to_dt(row['last_modified'])

                if current_lm > cached_lm:
                    logging.debug(f"Cached version of {file_.name} from {cached_lm} is out of date ({current_lm})")
                    to_index.append(file_)
                    # ensure we remember the last_modified
                    last_modified[file_] = current_lm

        logging.info(f"Refreshing {len(to_index)} files")
        
        metadata = indexer.index_files(to_index, processes)

        # cache metadata from collection sidecar files
        for file_ in sum(collection_sidecar_files.values(), start=[]):
            extra_metadata_cache.update(self.parse_extra_metadata(file_))
            parsed_collection_sidecar_files.add(file_)

        # add metadata to cache
        # metadata.keys() returns a list of all keys, but it's a multidict, so this might contain
        # duplicates, hence the set()
        for file_ in set(metadata.keys()):
            # obtain collection metadata for this file
            for fn in match_collection_sidecar_files(file_):
                if fn in parsed_collection_sidecar_files:
                    continue
                extra_metadata_cache.update(self.parse_extra_metadata(fn))
                parsed_collection_sidecar_files.add(fn)

            # start with collection metadata
            base_metadata = extra_metadata_cache.get(file_.parent, multidict.MultiDict()).copy()

            # apply sidecar file contents
            for sidecar in sidecar_files.get(file_, []):
                base_metadata.extend(stores.get(sidecar))

            # collect deletions
            delete_keys = {key_.split('.', 1)[1]
                           for key_, value in base_metadata.items()
                           if value is None and key_.startswith('extra.')}

            # apply metadata from the file itself
            base_metadata.extend(metadata[file_])

            for key_ in delete_keys | {shared.IS_RECURSIVE}:
                base_metadata.popall(key_, True)

            self.insert(file_, base_metadata, last_modified[file_])
            metadata[file_] = base_metadata

        return metadata

    def cleanup(self):
        """Find and remove all entries in the cache that refer to no longer existing files"""
        to_delete_ids = []

        for row in self.db.execute("select `id`, `path` from files"):
            path = pathlib.Path(row['path'])

            if not path.exists():
                to_delete_ids.append(row['id'])

        self.forget_ids(to_delete_ids)

    def clear(self):
        """Remove everything from the cache"""
        with self.db:
            self.db.execute("delete from metadata")
            self.db.execute("delete from files")

    def forget_ids(self, ids):
        """Delete these IDs from the cache"""
        with self.db:
            id_set = ", ".join(["?"]*len(ids))
            self.db.execute(f"delete from metadata where id in ({id_set})", ids)
            self.db.execute(f"delete from files where id in ({id_set})", ids)

    def expire_metadata(self, paths, recursive=True):
        """Remove all metadata associated to these paths

        But keep the paths in the database.
        """
        if paths is None:
            self.db.execute("update `files` set `last_modified` = ?", (sql.MIN_DATE,))
            return

        elif not isinstance(paths, list):
            paths = [paths]

        paths = [pathlib.Path(path).expanduser().resolve() for path in paths]

        query = 'update `files` set `last_modified` = ? where `path` in (' + \
                ", ".join(["?"]*len(paths)) + ")"
        self.db.execute(query, [sql.MIN_DATE] + [str(path) for path in paths])

    def forget(self, paths, recursive=True):
        """Remove all paths from the cache

        If recursive is True, all items in subdirectories are removed from the
        cache, too."""
        raise NotImplementedError()

    def find(self, query):
        """Find all items matching this query.

        query may either be a human-written search term or a Query instance.

        Returns a list to (path to file, metadata) tuples.
        """
        if query is None or len(query) == 0:
            query = Query()

        elif isinstance(query, str):
            query = Query.parse(query, self.config.synonyms)

        elif not isinstance(query, Query):
            raise TypeError()

        qry, args = query.as_sql()
        ids = [row['id'] for row in self.db.execute(qry, args)]
        
        return self._resolve_ids(ids)

    def get(self, paths, recursive=True):
        """Get metadata for all items of paths

        paths may also be a single path instead of a list of paths.

        If any element of paths is pointing to a directory and recursive is
        set to True, get will return the metadata for all elements inside
        that directory (and their subdirectories'), too.
        """
        if not isinstance(paths, list):
            paths = [paths]

        paths = [pathlib.Path(path).expanduser().resolve() for path in paths]
        
        args = [str(path) for path in paths if not path.is_dir()]
        if len(args) == 0:
            return []

        query = "select distinct `files`.`id` from `files` where `files`.`path` in (" \
                + ", ".join(["?"]*len(args)) + ")"

        ids = [row['id'] for row in self.db.execute(query, args)]

        return self._resolve_ids(ids)

    def keys(self):
        """Returns a set of all known metadata keys."""
        return {row['key'] for row in self.db.execute("select distinct `key` from `metadata`")}

    def insert(self, path, metadata, last_modified=None):
        """Insert the metadata for item at path into the cache.

        This operation will not modify the item in the filesystem nor update
        any other form of metadata persistency for the item.
        This function really only affects the cache.
        """
        # determine rowid, create new entry if there is none yet
        rowids = [row['id']
                 for row in self.db.execute("select `id` from `files` where `path` = ?",
                                            (str(path), ))]
        if last_modified is None:
            last_modified = shared.get_last_modified(path)

        if len(rowids) == 0:
            with self.db:
                result = self.db.execute("insert into `files`(`path`, `last_modified`) values(?, ?)",
                                         (str(path), sql.dt_to_str(last_modified)))
                rowid = result.lastrowid
            logging.debug(f"{path.name} not in cache yet. New ID is {rowid}")
        else:
            rowid = rowids[0]
            self.db.execute("update `files` set `last_modified` = ? where `id` = ?",
                            (sql.dt_to_str(last_modified), rowid))

        # clear existing metadata and write the current
        with self.db:
            self.db.execute("delete from `metadata` where `id` = ?", (rowid, ))

            for key in metadata.keys():
                if key in self.ignore_tags:
                    continue

                values = sum([value if isinstance(value, list) else [value]
                              for value in metadata.getall(key)
                              if value is not None], start=[])

                for value in values:
                    type_ = None
                    if isinstance(value, datetime.datetime):
                        type_ = Cache.TYPE_DATETIME
                        value = sql.dt_to_str(value)
                    elif isinstance(value, int):
                        type_ = Cache.TYPE_INT
                        value = str(value)
                    elif isinstance(value, float):
                        type_ = Cache.TYPE_FLOAT
                        value = str(value)
                    elif not isinstance(value, str):
                        logging.error(f"Unexpected type {type(value)} for key {key}, skipping")
                        continue
                    self.db.execute("insert into `metadata` values(?, ?, ?, ?)",
                                    (rowid, key, type_, value))

    def parse_extra_metadata(self, metafile):
        """Extract extra metadata from this file"""
        data = stores.get_for_collection(metafile)

        for filename in data.keys():
            data[filename][shared.IS_RECURSIVE] = data[filename][shared.IS_RECURSIVE] and \
                                                  self.recursive_extra_metadata
        
        return data

    def is_sidecar_file(self, path):
        """Determine whether the file at path is a sidecar file"""
        if not path.is_file:
            return False
        if path.name in self.collection_metadata:
            return True
        for store in stores.STORES:
            if path.suffix == store.SUFFIX and len([fn for fn in path.parent.iterdir() if fn.is_file() and fn != path and fn.stem == path.stem]) > 0:
                return True
        return False

    def _resolve_ids(self, ids):
        result = {}
        query = "select files.path, metadata.* from `files` " \
                " left join `metadata` on `files`.`id` = `metadata`.`id` " \
                " where `files`.`id` in (" + ", ".join(["?"]*len(ids)) + ")"
        for row in self.db.execute(query, ids):
            id_ = row['id']
            if id_ not in result:
                result[id_] = (row['path'], multidict.MultiDict())

            key, value = self._translate_row(row)
            if not isinstance(key, str):
                logging.error(f"Unexpected key type {type(key)}")
                key = str(key)
            result[id_][1].add(key, value)

        return [v for v in result.values()]

    def _translate_row(self, row):
        key, type_, value = row['key'], row['type'], row['value']
        
        if type_ == Cache.TYPE_DATETIME:
            value = sql.str_to_dt(value)
        elif type == Cache.TYPE_INT:
            value = int(value)
        elif type == Cache.TYPE_FLOAT:
            value = float(value)

        return key, value

    def _open_db(self):
        if self.db is not None:
            self.db.close()

        location = self.config.path('General', 'cache', configuration.CACHEPATH) / Cache.CACHE_FILENAME
        if not location.parent.exists():
            location.parent.mkdir(parents=True, exist_ok=True)

        self.db = sqlite3.connect(location)
        self.db.row_factory = sqlite3.Row
        self.db.create_function('REGEXP', 2, sql.regexp)

        with self.db:
            self.db.execute(sql.CREATE_FILE_TABLE)
            self.db.execute(sql.CREATE_META_TABLE)

    def _find_sidecar_files(self, files):
        """Find all sidecar files for these files

        Returns a dict with the mapping of path -> [sidecar files] containing
        all existing sidecar files"""
        sfiles = dict([(file_, [fn for fn in stores.sidecars_for(file_)
                                   if fn.exists()]) for file_ in files])
        return dict([pair for pair in sfiles.items() if len(pair[1]) > 0])

    def _find_collection_sidecar_files(self, files):
        """Find all collection sidecar files for these files

        Returns a dict with the mapping of path -> [sidecar files] containing
        all existing sidecar files"""
        queue = {f.parent for f in files}
        if self.recursive_extra_metadata:
            to_visit = set()
            # find all parent directories
            while len(queue) > 0:
                path = queue.pop()
                to_visit.add(path)
                if path.parent != path and path.parent not in to_visit:
                    queue.add(path.parent)
        sfiles = dict([(base, [base / fn for fn in self.collection_metadata
                                         if (base / fn).exists()])
                       for base in to_visit])
        return dict([pair for pair in sfiles.items() if len(pair[1]) > 0])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cache = Cache()
    breakpoint()

