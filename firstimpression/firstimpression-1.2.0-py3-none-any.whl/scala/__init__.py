"""scalascript.py - (C) Scala

A module to provide Python 3 compatibility with the Scala Linux Player's
embedded Python module.
"""
from copy import deepcopy
try:
    from collections.abc import MutableMapping, MutableSequence
except ImportError:
    from collections import MutableMapping, MutableSequence
import win32api
import win32com.client
import pythoncom
import logging
import traceback
import struct
import os
from firstimpression.constants import NAMELEVEL

if not os.name == 'nt':
    raise ImportError('This module is intended for Microsoft Windows only.')

import sys
import inspect

# Don't allow importing from the command line or interactive interpreter
# as this module simulates the Linux Player's built-in scalascript
# module and shouldn't be available.

# Scala COM handles, initialized on demand
_scalaplayer = None
_infoplayer = None

# ActiveX ProgIDs
_prog_id_scalaplayer = 'ScalaPlayer.ScalaPlayer.1'
_prog_id_infoplayer5 = 'Scala.InfoPlayer5'
_prog_id_filelock = 'ScalaFileLock.ScalaFileLock.1'
_prog_id_netic = 'Scala.InfoNetwork'


def _hresult_as_hex(hr):
    # Courtesy of: https://stackoverflow.com/a/10641263/100955
    return struct.unpack("L", struct.pack("l", hr))[0]


class variables(MutableMapping):
    """This class matches the API baked-in on the Linux Player. It 
    behaves like a dictionary. Unlike the Python 2 implementation, this
    class provides access to ALL non-hidden ScalaScript variables, and 
    with their original names.

    Behavior that differs from sharedvars:
        - Does not handle default values
        - Raises KeyError when getting variables that don't exist
        - Only the shared variables are available in this dictionary,
          and NOT all global namespace items

    Behavior that differs from Linux player:
        - Any Explicitly shares Scala vars continue to be available in 
          the main namespace. Watch out for clobbering them!

    Example::

        import scalascript
        svars = scalalib.variables()
        f = file(svars['filename'])       # get value
        svars['result'] = 15              # set value

    """

    class array(MutableSequence):
        """Needs to behave like other mutable types."""

        def __init__(self, key):
            self._key = key

            # Start up the COM interface
            global _scalaplayer
            if not _scalaplayer:
                _scalaplayer = win32com.client.Dispatch(_prog_id_scalaplayer)
            self._scalaplayer = _scalaplayer

        def __repr__(self):
            item = None
            try:
                item = self._scalaplayer.GetScalaScriptValue(self._key)
            except Exception as err:
                log(logging.ERROR, str(err))

            return list(item)

        def __str__(self):
            return str(self.__repr__())

        def __getitem__(self, index):
            item = self.__repr__()
            return item[index]

        def __setitem__(self, index, value):
            log(logging.DEBUG, "Setting %s[%s] to %s", self._key, index, value)
            item = self.__repr__()
            item[index] = value
            try:
                self._scalaplayer.SetScalaScriptValue(self._key, tuple(item))
            except Exception as err:
                log(logging.ERROR, str(err))

        def __delitem__(self, index):
            raise IndexError("deleting ScalaScript array items is not allowed")

        def __len__(self):
            return len(self.__repr__())

        def insert(self, index, value):
            raise IndexError(
                "inserting ScalaScript array items is not allowed")

        def clear(self):
            raise IndexError("deleting ScalaScript array items is not allowed")

        def extend(self, values):
            raise IndexError(
                "extending ScalaScript array items is not allowed")

        def pop(self, index=-1):
            raise IndexError("deleting ScalaScript array items is not allowed")

        def remove(self, value):
            raise IndexError("removing ScalaScript array items is not allowed")

    def __init__(self, defaults=None):
        # Start up the COM interface
        global _scalaplayer
        if not _scalaplayer:
            _scalaplayer = win32com.client.Dispatch(_prog_id_scalaplayer)
        self._scalaplayer = _scalaplayer

        # Copy the defaults dict
        if defaults:
            self._defaults = deepcopy(defaults)
        else:
            self._defaults = {}

    def __delitem__(self, key):
        """Can't delete, move along."""
        pass

    def __iter__(self):
        for key in self._scalaplayer.ListScalaScriptValues():
            yield key

    def keys(self):
        return self._scalaplayer.ListScalaScriptValues()

    def __len__(self):
        return len(self._scalaplayer.ListScalaScriptValues())

    def __getitem__(self, key):
        item = None

        if key in self._scalaplayer.ListScalaScriptValues():
            try:
                item = self._scalaplayer.GetScalaScriptValue(key)
                if type(item) in (tuple, list):
                    item = self.array(key)
            except Exception as err:
                log(logging.ERROR, str(err))
        else:
            # Look in the defaults dict
            # Allow any KeyError here to be raised
            item = self._defaults[key]

        return item

    def __setitem__(self, key, item):
        """Set new values for existing items only.  Drop any newly added 
        values.
        """
        if self[key] is None:
            return

        result = None
        try:
            if type(item) in (tuple, list):
                # Create a scalascript.variables.array and set the new
                # values iteratively
                _array = self.array(key)
                for i, element in enumerate(item):
                    _array[i] = element
            else:
                # Assign the value
                result = self._scalaplayer.SetScalaScriptValue(key, item)
        except Exception as err:
            log(logging.ERROR, str(err))

    def items(self):
        for key in self.keys():
            yield key, self.__getitem__(key)

    def __contains__(self, key):
        return (key in self._scalaplayer.ListScalaScriptValues())


def find_content(scalapath):
    r"""Find platform path to versionated files via Scala-style virtual path.

    Note: 
        Windows and Linux require differently-formatted Scala paths.
        This function will convert appropriately, while the Linux player
        WILL NOT:

            # Works on Windows and Linux
            local_path = scalascript.getfilepath("Content://findme.txt")

            # Will not work on Linux
            local_path = scalascript.getfilepath("Content:\\findme.txt")

        Be mindful of case-sensitivity issues.

        Under the hood, this function calls LockScalaFile, and 
        UnlockScalaFile when the returned object goes out of scope.

    Args:
        scalapath (str): Scala-formatted path

    Returns:
        str: local filesystem path to versionated file.
    """
    # PyErr_SetString(PyExc_TypeError, "path must be a string");
    if not isinstance(scalapath, str):
        raise TypeError("path must be a string")

    _path = scalapath.replace("//", "\\")
    platform_path = _lock_content(_path)
    if platform_path:
        return platform_path
    else:
        raise FileNotFoundError(
            'The path "{}" does not exist.'.format(scalapath))


def install_content(abspath, subfolder=None):
    r'''Copies a file to the local Scala Content: folder.

    Note: Assumes netic service is already running!

    Args:
        abspath (str): A file (specified by its absolute path) to copy.
        subfolder (str): Place it into a subfolder to group related files.
    Notes:
        Installed files may be found later using a Scala-style virtual path
        string via find_content::

            find_content(r'Content://filename.ext')

    Returns:
        str: platform path to content, as installed and versionated.
    '''
    if not os.path.exists(abspath):
        raise FileNotFoundError('File "{}" does not exist.'.format(abspath))

    if not subfolder:
        subfolder = ''

    try:
        netic = win32com.client.Dispatch(_prog_id_netic)
        netic.IntegrateContentLocally(abspath, subfolder)
        log(logging.INFO, abspath)

        if subfolder:
            where_it_should_be = 'Content://' + \
                subfolder + '/' + os.path.basename(abspath)
        else:
            where_it_should_be = 'Content://' + os.path.basename(abspath)

        return find_content(where_it_should_be)

    except pythoncom.com_error as err:
        errstr = '{}\n\nPlayer Transmission Client ({}) not available.'.format(
            str(err), _prog_id_netic)
        log(logging.error, errstr.replace('\n', '  '))
        raise RuntimeError(errstr)
    except Exception as err:
        log(logging.error, str(err))


def _lock_content(scalapath, report_err=True):
    r"""Locks a content file so the player doesn't try to remove it.

    Args:
        scalapath (str): Scala-style virtual path, such as "Content://file.ext"
        report_err (bool): Log errors?

    Returns:
        str: The Windows path to the affected file.
             If the file is not found or there is an error, returns None.
    """
    class _StringAndLock(str):
        """A subclass of a string that carries a Scala lock object around with
        it.  The lock will be unlocked upon deletion when the object falls out of
        scope or is deleted explicitly.
        """

        def __del__(self):
            if hasattr(self, 'lockObj'):
                log(logging.DEBUG, 'unlock_content: "{}"'.format(scalapath))
                self.lockObj.UnlockScalaFile()

    try:
        lockObj = win32com.client.Dispatch(_prog_id_filelock)
        windows_path = lockObj.LockScalaFile(scalapath)

        # Add the lock into the string, to unlock upon its deletion.
        windows_path = _StringAndLock(windows_path)
        windows_path.lockObj = lockObj

        log(logging.INFO, '"{}" @ "{}"'.format(scalapath, windows_path))

        return windows_path
    except Exception as err:
        if report_err:
            log(logging.ERROR, str(err))
        return None


def log(level, msg, *args, **kwargs):
    """This logging method is meant to mimic the way the Linux Player 
    handles logging, and does not work the way Windows scalalib-based
    logging previously did. 

    Behavior that differs from Linux player:
        As the method made available via ActiveX does not allow for
        setting the loglevel, all messages are forced to "INFO".

        The Python2 scalalib module's logging.Handler inserted the
        loglevel and scope on an INFO line before the message, that
        behavior has been duplicated.

    Args:
        level (logging.loglevel): Somewhat ignored, but is inserted.
                                  See behvior notes above.
        msg (str): message to log in Python logging module format
        args: arguments for format string
        exc_info (bool, exception): Mimics logging module behavior.

    Note:
        This is not a full logging module object!
    """
    global _scalaplayer
    if not _scalaplayer:
        _scalaplayer = win32com.client.Dispatch(_prog_id_scalaplayer)

    try:
        attr_dict = {}
        attr_dict['level'] = level
        attr_dict['msg'] = msg
        attr_dict['args'] = args

        _exc_text = None
        exc_info = kwargs.get('exc_info')
        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()

            attr_dict['exc_info'] = exc_info
            _exc_text = traceback.format_exception(*exc_info)

        _formatted_msg = logging.makeLogRecord(attr_dict).getMessage()
        if _exc_text:
            if _formatted_msg[-1:] != "\n":
                _formatted_msg += "\n"
            _formatted_msg += ''.join(_exc_text).strip()

        _caller = inspect.currentframe().f_back.f_code.co_name
        _level_name = logging.getLevelName(level)
        _scalaplayer.Log("{} {}: {}".format(
            _level_name, _caller, _formatted_msg))

    except pythoncom.com_error as err:
        # Do not attempt to log while logging is in an error state!
        # Not sure where this print actually goes, though.
        print('COM Error: {}'.format(err))


def quitplayer():
    """Send Quit Request to Scala Player.

    Returns:
        bool: False on failure
    """
    global _infoplayer
    try:
        # Comment from scalalib: don't cache obj, doesn't work more than once
        _infoplayer = win32com.client.Dispatch(_prog_id_infoplayer5)
        log(logging.DEBUG, 'Attempting to quit...')
        _infoplayer.Quit()
        return True
    except pythoncom.com_error as err:
        errstr = '{}\n\nScala Player ({}) not available.'.format(
            str(err), _prog_id_infoplayer5)
        log(logging.ERROR, errstr.replace('\n', '  '))
    except Exception as err:
        log(logging.ERROR, err)

    return False


def restartplayback():
    """Send Restart Playback request to Scala Player.

    Returns:
        bool: False on failure
    """
    global _infoplayer
    try:
        # Comment from scalalib: don't cache obj, doesn't work more than once
        _infoplayer = win32com.client.Dispatch(_prog_id_infoplayer5)
        log(logging.DEBUG, 'Attempting to restart playback...')
        _infoplayer.RestartPlayback()
        return True
    except pythoncom.com_error as err:
        errstr = '{}\n\nScala Player ({}) not available.'.format(
            str(err), _prog_id_infoplayer5)
        log(logging.ERROR, errstr.replace('\n', '  '))
    except Exception as err:
        log(logging.ERROR, err)

    return False


def sleep(secs):
    """Sleep lightly for a number of seconds while maintaining awareness of 
    whether or not playback has been aborted.

    Note:
        Follows the Python convention and takes SECONDS, not milliseconds. 
        This makes it easier to conditionally import scalascript.sleep or 
        time.sleep for command-line testing.

    Raises:
        KeyboardInterrupt

    Args:
        secs (float): fractional seconds
    """
    DISP_E_EXCEPTION = 0x80020009
    E_ABORT = 0x80004004

    global _scalaplayer
    if not _scalaplayer:
        _scalaplayer = win32com.client.Dispatch(_prog_id_scalaplayer)

    try:
        _scalaplayer.Sleep(secs * 1000)
    except pythoncom.com_error as err:
        # On abort, raise KeyboardInterrupt, like the Linux Player does
        # when it receives SIGINT.
        # scalalib.sleep() would call sys.exit(9)

        # Need to check main hresult and the exception info, as the main hresult
        # may just be an iDispatch general error.
        if _hresult_as_hex(err.hresult) == E_ABORT:
            raise KeyboardInterrupt
        elif _hresult_as_hex(err.hresult) == DISP_E_EXCEPTION and _hresult_as_hex(err.excepinfo[-1]) == E_ABORT:
            raise KeyboardInterrupt
        else:
            raise

class Log:
    def __init__(self, name, script):
        self.name = name
        self.level = NAMELEVEL[name]
        self.script = script
        try:
            self.debug = variables()['Player.debug_python']
        except KeyError:
            self.debug = False
    
    def log(self, msg):
        if (self.level == NAMELEVEL['DEBUG'] and self.debug) or not self.level == NAMELEVEL['DEBUG']:
            log(self.level, '{}: {}'.format(self.script, msg))

