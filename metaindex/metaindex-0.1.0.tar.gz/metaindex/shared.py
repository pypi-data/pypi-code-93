"""Functions, names, and identifiers shared in the code"""
import datetime


IS_RECURSIVE = 'extra_metadata_is_recursive'
LAST_MODIFIED = 'extra_metadata_last_modified'


def get_last_modified(file_):
    """Return the last_modified datetime of the given file.

    This will drop the microsecond part of the timestamp! The reasoning is that
    last_modified will be taken during database cache updates. If a change
    happens at the same second to a file, just after the indexer passed it,
    there's probably a good chance the file gets modified again in the near
    future at which point the indexer will pick up the change.
    Other than that, the cache can forcefully be cleared, too.
    """
    return datetime.datetime.fromtimestamp(file_.stat().st_mtime).replace(microsecond=0)

