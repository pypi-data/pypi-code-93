import logging
import argparse
import sys
import os
import pathlib
import mimetypes
import json
import shutil
import shlex
import subprocess
import tempfile

from metaindex import configuration
from metaindex import stores
from metaindex.cache import Cache
from metaindex.find import find

try:
    from metaindex.fuse import metaindex_fs
except ImportError:
    metaindex_fs = None


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config',
                        default=None,
                        type=str,
                        help="The configuration file to use. Defaults "
                            f"to {configuration.CONFIGFILE}.")

    parser.add_argument('-l', '--log-level',
                        default='warning',
                        choices=['debug', 'info', 'warning', 'error', 'fatal'],
                        help=f"The level of logging. Defaults to %(default)s.")

    subparsers = parser.add_subparsers(dest='command')

    indexparser = subparsers.add_parser('index')

    indexparser.add_argument('-r', '--recursive',
                             default=False,
                             action='store_true',
                             help='Go through all subdirectories of any paths')

    indexparser.add_argument('-f', '--force',
                             default=False,
                             action="store_true",
                             help="Enforce indexing, even if the files on disk "
                                  "have not changed.")

    indexparser.add_argument('-m', '--flush-missing',
                             default=False,
                             action="store_true",
                             help="Remove files from cache that can no longer be "
                                  "found on disk.")

    indexparser.add_argument('-i', '--index',
                             nargs='*',
                             type=str,
                             help="Path(s) to index. If you provide none, all "
                                  "cached items will be refreshed. If you pass "
                                  "- the files will be read from stdin, one "
                                  "file per line.")

    indexparser.add_argument('-p', '--processes',
                             type=int,
                             default=None,
                             help="Number of indexers to run at the same time. "
                                  "Defaults to the number of CPUs that are available.")

    indexparser.add_argument('-C', '--clear',
                             default=False,
                             action='store_true',
                             help="Remove all entries from the cache")

    findparser = subparsers.add_parser('find')

    findparser.add_argument('-t', '--tags',
                            nargs='*',
                            help="Print these metadata tags per file, if they "
                                 "are set. If you provide -t, but no tags, all "
                                 "will be shown.")

    findparser.add_argument('-f', '--force',
                            default=False,
                            action='store_true',
                            help="When creating symlinks, accept a non-empty "
                                 "directory if it only contains symbolic links.")

    findparser.add_argument('-l', '--link',
                            type=str,
                            default=None,
                            help="Create symbolic links to all files inside "
                                 "the given directory.")

    findparser.add_argument('-k', '--keep',
                            default=False,
                            action='store_true',
                            help="Together with --force: do not delete existing "
                                 "links but extend with the new search result.")

    findparser.add_argument('query',
                            nargs='*',
                            help="The search query. If the query is - it will "
                                 "be read from stdin.")

    addparser = subparsers.add_parser('add')
    addparser.add_argument('-t', '--tag',
                           nargs="+",
                           type=str,
                           help="Tags to add in the form of 'tag:value'")

    addparser.add_argument('-a', '--all',
                           default=False,
                           action='store_true',
                           help="Add tags to all current and future files in the "
                                "given directories.")

    addparser.add_argument('-r', '--recursive',
                           default=False,
                           action="store_true",
                           help="In combination with `-a', add tags also to all "
                                "subdirectories.")

    addparser.add_argument('-u', '--update-cache',
                           default=False,
                           action="store_true",
                           help="Update the cache after the changes.")

    addparser.add_argument('paths',
                           nargs='*',
                           help="Paths that should receive these tags")

    removeparser = subparsers.add_parser("remove")
    removeparser.add_argument("-t", "--tags",
                              nargs='*',
                              type=str,
                              help="The tags to remove (case-sensitive).")
    removeparser.add_argument("-r", "--recursive",
                              default=False,
                              action="store_true",
                              help="Recursively remove the tags also in "
                                   "all subdirectories.")
    removeparser.add_argument("-x", "--extra",
                              default=False,
                              action="store_true",
                              help="Remove all user-provided extra metadata.")
    removeparser.add_argument("-u", "--update-cache",
                              default=False,
                              action="store_true",
                              help="Update the cache after removing the tags.")
    removeparser.add_argument("paths",
                              nargs="+",
                              type=str,
                              help="The files and/or directories to remove the "
                                   "tags from.")

    editparser = subparsers.add_parser("edit")
    editparser.add_argument('files',
                            nargs='+',
                            type=str,
                            help="The files of which you want to edit the "
                                 "metadata.")

    if metaindex_fs is not None:
        fsparser = subparsers.add_parser('fs')
        
        fsparser.add_argument('action',
                              choices=('mount', 'unmount', 'umount'),
                              help="The command to control the filesystem")
        fsparser.add_argument('mountpoint',
                              type=str,
                              help="Where to mount the metaindex filesystem.")

    result = parser.parse_args()

    if result.command is None:
        parser.print_help()

    return result


def collect_files_and_metadata(config, paths, expand=False, recursive=False):
    """Find all files and metadata sidecar files for this set of paths

    Returns a tuple (paths, metadata); paths is the (potentially expanded)
    list of paths and metadata is a dict:
    metadatafile: pathlib.Path -> dict of extra metadata (as read from the
    metadata sidecar file(s) if it existed)
    """
    queue = [pathlib.Path(path).expanduser().resolve() for path in paths]
    paths = set()
    metadata = {}

    while len(queue) > 0:
        path = queue.pop(0)

        if not path.is_file() and not path.is_dir():
            logging.error(f"{path} is neither file nor directory. Skipping.")
            continue

        metafile = config.sidecar_for(path)

        if metafile not in metadata and metafile.is_file():
            metadata[metafile] = stores.get_for_collection(metafile)

        if metafile not in metadata:
            metadata[metafile] = {}

        if path.is_dir():
            queue += [that for that in path.iterdir()
                      if (that.is_dir() and recursive) or (that.is_file() and expand)]
            paths.add(path)
            continue

        if path == metafile:
            continue

        paths.add(path)

    return list(paths), metadata


def run():
    logging.basicConfig(level=logging.WARNING,
                        format="[%(levelname)s] %(message)s")
    args = parse_args()

    logging.getLogger().setLevel(args.log_level.upper())

    config = configuration.load(args.config)

    extra_mimetypes = [pathlib.Path(fn.strip()).expanduser().resolve()
                       for fn in config.list('General', 'mimetypes', "", "\n")]
    if len(extra_mimetypes) > 0:
        mimetypes.init(extra_mimetypes)

    if args.command == "index":
        cache = Cache(config)
        if args.clear:
            cache.clear()
        if args.flush_missing:
            cache.cleanup()

        index = args.index
        if index == ['-']:
            index = [file_ for file_ in sys.stdin.read().split("\n") if len(file_) > 0]

        elif index == []:
            index = None

        if args.force:
            cache.expire_metadata(index)

        cache.refresh(index, args.recursive, args.processes)

        return 0

    elif args.command == "find":
        return find(config, args)

    elif args.command == "remove":
        # TODO - handle file specific sidecar files, too
        paths, metadata = collect_files_and_metadata(config,
                                                     args.paths,
                                                     expand=True,
                                                     recursive=args.recursive)
        tags = sum([config.synonyms.get(tag, [tag]) for tag in args.tags], start=[])
        for path in paths:
            metafile = config.sidecar_for(path)
            if path.is_file():
                targets = [path.name]

            for target in targets:
                if metafile in metadata:
                    if path.name not in metadata[metafile]:
                        metadata[metafile][target] = {}
                else:
                    metadata[metafile] = {target: {}}

                for tag in tags:
                    metadata[metafile][target][tag] = None

        for metafile in metadata.keys():
            data = metadata[metafile]
            metafile.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))

        if args.update_cache:
            paths = {metafile.parent for metafile in metadata.keys()}
            cache = Cache(config)
            cache.refresh(paths)

    elif args.command == "add":
        new_tags = [value.split(':', 1) for value in args.tag if ':' in value]
        # TODO - handle file specific sidecar files, too
        paths, metadata = collect_files_and_metadata(config,
                                                     args.paths,
                                                     not args.all,
                                                     (not args.all) and args.recursive)

        for path in paths:
            metafile = config.sidecar_for(path)

            if path.is_file():
                target = str(path.name)
            else:
                if args.all and args.recursive:
                    target = '**'
                elif args.all:
                    target = '*'
                else:
                    continue

            if target not in metadata[metafile]:
                metadata[metafile][target] = {}

            data = metadata[metafile][target]
            
            for tag, value in new_tags:
                if tag not in data or data[tag] is None:
                    metadata[metafile][target][tag] = value

                elif not isinstance(data[tag], list):
                    data[tag] = [data[tag]]

                if isinstance(data[tag], list):
                    data[tag].append(value)

        for metafile in metadata.keys():
            data = metadata[metafile]
            metafile.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))

        if args.update_cache:
            paths = {metafile.parent for metafile in metadata.keys()}
            cache = Cache(config)
            cache.refresh(paths)

    elif args.command == 'edit':
        files = [pathlib.Path(path).expanduser().resolve() for path in args.files]
        files = [file_ for file_ in files if file_.is_file()]
        editor = None
        for name in ['VISUAL', 'EDITOR']:
            value = os.getenv(name)
            if value is None:
                continue
            editor = shutil.which(value)
            if editor is not None:
                break
        if editor is None:
            logging.fatal(f"Don't know what editor to use.")
            return -1
        editor = shlex.split(editor)

        cache = Cache(config)
        cache.refresh(files)

        metadata = {}
        for path, mdata in cache.get(files):
            metadata[path] = dict([(k.split('.', 1)[1], mdata.popall(k))
                                   for k in list(mdata.keys())
                                   if k.startswith('extra.')])

        with tempfile.NamedTemporaryFile("w+t", encoding="utf-8", suffix=".json") as tmpfd:
            tmpfd.write(json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True))
            tmpfd.flush()
            subprocess.run(editor + [tmpfd.name])
            tmpfd.flush()
            tmpfd.seek(0)
            updated = json.loads(tmpfd.read())

        metafile_cache = {}
        raise NotImplementedError("Currently defunct - must use metaindex.stores to function properly")
        for fn in metadata.keys():
            if fn not in updated:
                continue
            extra = updated[fn]
            fnpath = pathlib.Path(fn)
            to_write = {fnpath.name: extra}
            metafile = config.resolve_sidecar_for(fnpath)
            if metafile not in metafile_cache:
                metafile_cache[metafile] = {}
                if metafile.is_file():
                    metafile_cache[metafile] = json.loads(metafile.read_text())
            metafile_cache[metafile][fnpath.name] = extra

        for metafile in metafile_cache.keys():
            metafile.write_text(json.dumps(metafile_cache[metafile], indent=2, ensure_ascii=False, sort_keys=True))

        cache.refresh(files)

    elif args.command == 'fs' and metaindex_fs is not None:
        return metaindex_fs(config, args)

    return -1

