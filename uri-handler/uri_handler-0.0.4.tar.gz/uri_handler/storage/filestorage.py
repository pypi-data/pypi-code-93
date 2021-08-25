"""
filesystem-based uri utilities
"""
import errno
import os

import atomicwrites

from uri_handler.utils._compat import (
    urllib,
    pathlib)


def file_readbytes(fn):
    with open(fn, 'rb') as f:
        b = f.read()
    return b


def makedirs_safe(d):
    try:
        os.makedirs(d)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def atomic_file_writebytes(b, fn, overwrite=False):
    with atomicwrites.AtomicWriter(
            fn, mode='wb', overwrite=overwrite).open() as f:
        f.write(b)


def nonatomic_file_writebytes(b, fn, overwrite=False):
    m = 'wb' if overwrite else 'xb'

    with open(fn, m) as f:
        f.write(b)


def file_writebytes(b, fn, atomic=False, make_outdir=True, overwrite=True):
    if make_outdir:
        makedirs_safe(os.path.dirname(fn))

    if atomic:
        return atomic_file_writebytes(b, fn, overwrite=overwrite)
    else:
        return nonatomic_file_writebytes(b, fn, overwrite=overwrite)


def get_available_space_percentage(d):
    s = os.statvfs(d)
    return float(s.f_bavail) / float(s.f_blocks)


def get_used_space_percentage(d):
    return 1. - get_available_space_percentage(d)


def get_available_space_bytes(d):
    s = os.statvfs(d)
    return s.f_bavail * s.f_frsize


def uri_to_filename(uri):
    return urllib.parse.unquote(urllib.parse.urlparse(str(uri)).path)


def filename_to_uri(fn):
    return pathlib.Path(fn).as_uri()


def listfiles_from_dir(d, full=True):
    if not full:
        raise NotImplementedError("relative path returns not implemented")
    for i in os.listdir(d):
        ifull = os.path.join(d, i)
        if os.path.isdir(i):
            # yield from listfiles_from_dir(ifull)
            for it in listfiles_from_dir(ifull):
                yield it
        else:
            yield ifull


def file_listuris_from_prefix(uri):
    d = uri_to_filename(uri)
    fpaths = listfiles_from_dir(d, full=True)
    for fpath in fpaths:
        yield filename_to_uri(fpath)


def get_deep_directory_exists(d):
    if os.path.isdir(d):
        return d
    else:
        newd = os.dirname(d)
        # special values '/' and ''
        if newd == d:
            return newd
        else:
            return get_deep_directory_exists(newd)


def file_validate_prefix(uri, check_writable=True, **kwargs):
    d = uri_to_filename(uri)

    # get deepest existing directory
    d_exist = get_deep_directory_exists(d)
    if check_writable:
        if not os.access(d_exist, os.W_OK | os.X_OK):
            return False
    return True


class FileUriHandler:
    atomic = True
    make_outdir = True
    overwrite = True

    def save_bytes(self, b, uri):
        return file_writebytes(
            b, uri_to_filename(uri),
            self.atomic, self.make_outdir, self.overwrite)

    def write_bytes(self, uri, b):
        return self.save_bytes(b, uri)

    def read_bytes(self, uri):
        return file_readbytes(uri_to_filename(uri))

    def list_uris_prefix(self, uri_prefix):
        return file_listuris_from_prefix(uri_prefix)

    def validate_prefix(self, uri_prefix, **kwargs):
        return file_validate_prefix(uri_prefix)
