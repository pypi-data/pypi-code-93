#! /usr/bin/env python3

# from tendo project
# https://github.com/pycontribs/tendo

import logging
from multiprocessing import Process
import os
import sys
import tempfile
import unittest
import warnings

from typing import Optional


if sys.platform != "win32":
    import fcntl


class SingleInstanceException(BaseException):
    pass


class SingleInstance(object):
    def __init__(self, flavor_id: Optional[str] = None, lockfile: Optional[str] = None):
        warnings.simplefilter("ignore", ResourceWarning)
        self.initialized = False
        if flavor_id is None and lockfile is None:
            logger.error("Either 'flavor_id' or 'lockfile' is required, quitting.")
            raise SingleInstanceException()
        if lockfile is not None:
            self.lockfile = lockfile
        else:
            basename = sys.argv[0]
            basename = os.path.abspath(basename)
            basename = os.path.splitext(basename)[0]
            basename = basename.replace("\\", "-").replace("/", "-").replace(":", "").strip("-")
            basename = f"{basename}-{flavor_id}.lock"
            self.lockfile = os.path.join(tempfile.gettempdir(), basename)

        logger.debug("SingleInstance lockfile: " + self.lockfile)
        if sys.platform == 'win32':
            try:
                # file already exists, we try to remove (in case previous
                # execution was interrupted)
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile)
                self.fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            except OSError:
                _, e, _ = sys.exc_info()
                if e.errno == 13:
                    logger.error("Another instance is already running, quitting.")
                    raise SingleInstanceException()
                print(e.errno)
                raise
        else:  # non Windows
            self.fp = open(self.lockfile, 'w')
            self.fp.flush()
            try:
                fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                logger.warning("Another instance is already running, quitting.")
                raise SingleInstanceException()
        self.initialized = True

    def __del__(self):
        if not self.initialized:
            return
        try:
            if sys.platform == 'win32':
                if hasattr(self, 'fd'):
                    os.close(self.fd)
                    os.unlink(self.lockfile)
            else:
                fcntl.lockf(self.fp, fcntl.LOCK_UN)
                # os.close(self.fp)
                if os.path.isfile(self.lockfile):
                    os.unlink(self.lockfile)
        except Exception as e:
            if logger:
                logger.warning(e)
            else:
                print("Unloggable error: %s" % e)
            sys.exit(-1)


def f(name):
    tmp = logger.level
    logger.setLevel(logging.CRITICAL)  # we do not want to see the warning
    try:
        me2 = SingleInstance(flavor_id=name)  # noqa
    except SingleInstanceException:
        sys.exit(-1)
    logger.setLevel(tmp)


class TestSingleton(unittest.TestCase):
    def test_1(self):
        me = SingleInstance(flavor_id="test-1")
        del me  # now the lock should be removed
        assert True

    def test_2(self):
        p = Process(target=f, args=("test-2",))
        p.start()
        p.join()
        # the called function should succeed
        assert p.exitcode == 0, "%s != 0" % p.exitcode

    def test_3(self):
        me = SingleInstance(flavor_id="test-3")  # noqa -- me should still kept
        p = Process(target=f, args=("test-3",))
        p.start()
        p.join()
        # the called function should fail because we already have another
        # instance running
        assert p.exitcode != 0, "%s != 0 (2nd execution)" % p.exitcode
        # note, we return -1 but this translates to 255 meanwhile we'll
        # consider that anything different from 0 is good
        p = Process(target=f, args=("test-3",))
        p.start()
        p.join()
        # the called function should fail because we already have another
        # instance running
        assert p.exitcode != 0, "%s != 0 (3rd execution)" % p.exitcode

    def test_4(self):
        lockfile = '/tmp/foo.lock'
        me = SingleInstance(lockfile=lockfile)
        assert me.lockfile == lockfile


logger = logging.getLogger("tendo.singleton")


if __name__ == "__main__":
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    unittest.main()
