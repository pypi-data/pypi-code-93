
'''Tools for Bright Edge eServices developments & projects

Designed for the use in the Bright Edge eServices echo system. It defines
methods and functions for general use purposes.

Archiver creates an archive of the key project files, print coloured messages
to console with default parameters.

To Do
=====
1. Better example on the logging integration.
2. Complete doctests for all methods & functions.

'''

import datetime
import logging
import os
import zipfile
from pathlib import Path
import shutil
import sys
import tempfile
from termcolor import colored

_PROJ_DESC = __doc__.split('\n')[0]
_PROJ_PATH = Path(__file__)
_PROJ_NAME = _PROJ_PATH.stem
_PROJ_VERSION = '3.3.0'


class Archiver:
    '''Archiver creates an archive of the key project files to zip file. It assumes the
    following project structure of the caling application:

    Module
    ======
    projectname/ (a.k.a. Project root dir)
    │
    ├── Data/
    │
    ├── docs/
    │
    ├── src/ (a.k.a. Source dir)
    │   └── modname (a.k.a. Project dir)
    │       ├── module1.py
    │       └── module2.py
    │
    ├── tests/
    │   ├── test_module1_test_name1.py
    │   └── test_module1_test_name2.py
    │
    ├── .gitignore
    ├── LICENSE
    ├── README.md
    ├── requirements.txt
    └── setup.py

    Package
    ======
    projectname/ (a.k.a. Project root dir)
    │
    ├── Data/
    │
    ├── docs/
    │
    ├── pkgname/ (a.k.a. Project dir)
    │   ├── __init__.py
    │   ├── file1.py
    │   └── file2.py
    │
    ├── tests/
    │   ├── test_file1_test_name.py
    │   └── test_file2_test_name.py
    │
    ├── .gitignore
    ├── LICENSE
    ├── README.md
    ├── requirements.txt
    └── setup.py

    Library (not implemented)
    =======
    projectname/
    │
    ├── docs/
    │
    ├── Data/
    │
    ├── libname/
    │   ├── __init__.py
    │   ├── file_1.py
    │   ├── pkg_1/
    │   │   ├── __init__.py
    │   │   ├── file_1.py
    │   │   └── file_2.py
    │   │
    │   └── pkg_2/
    │       ├── __init__.py
    │       ├── file_3.py
    │       └── file_4.py
    │
    ├── tests/
    │
    ├── .gitignore
    ├── LICENSE
    ├── README.md
    ├── requirements.txt
    └── setup.py
    '''

    def __init__(
        self,
        p_parent_log_name,
        p_app_ver,
        p_app_desc,
        p_app_pth,
        p_app_ini_file_name=None,
        p_cls=True,
        p_logger = False,
        p_arc_excl_dir = None,
        p_arc_extern_dir = None,
        p_arc_incl_ext = None
    ):
        '''Initialize the object

        Parameters
        ----------
        p_parent_log_name
            Name of the parent logger, i.e., calling application
        p_app_ver
            Version of the calling application
        p_app_desc
            Description of the calling application
        p_app_pth
            Path to the application module
        p_app_ini_file_name
            Ini file name used by calling application for paramenters
            Default = None
        p_cls
            Clear the screen before start
            Default = True

        Returns
        -------

        Examples
        --------
        >>> au = Archiver(_PROJ_NAME, _PROJ_VERSION, __doc__, p_app_pth=Path(__file__))
        >>>

        '''

        self.success = True
        if p_logger:
            self.log_name = '{}.{}'.format(p_parent_log_name, _PROJ_NAME)
            self.logger = logging.getLogger(self.log_name)
        else:
            self.log_name = None
            self.logger = None
        if not isinstance(p_app_pth, Path):
            self.app_pth = Path(p_app_pth)
        else:
            self.app_pth = p_app_pth

        self.app_desc = p_app_desc
        self.app_ini_file_name = p_app_ini_file_name
        self.app_name = self.app_pth.stem
        self.app_ver = p_app_ver
        self.app_root_dir = self.find_app_root_dir()
        self.arc_dir = None
        self.arc_excl_dir = _add_parm(['Archive', 'VersionArchive', 'build'], p_arc_excl_dir)
        if p_arc_extern_dir:
            self.arc_extern_dir = Path(p_arc_extern_dir)
        else:
            self.arc_extern_dir = None
        self.arc_incl_ext = _add_parm(['ini', 'py'], p_arc_incl_ext)
        self.arc_pth = None
        self.cls = p_cls
        self.dur_hours = 0
        self.dur_min = 0
        self.dur_sec = 0
        self.elapsed_time = 0
        self.end_time = 0
        self.start_time = datetime.datetime.now()
        self.start_date_str = self.start_time.strftime('%y%m%d%H%M%S')
        self.version_archive = 'VersionArchive'

        self.make_archive()
        self.make_archive_external()
        pass

    def is_dev_mode(self):
        '''Determine if it is a production module or not.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------

        '''
        success = False
        if 'site-packages' not in self.app_pth.parts:
            success = True
        return success

    def find_app_root_dir(self):
        app_root_dir = None
        if 'src' in self.app_pth.parts:
            idx = self.app_pth.parts.index('src')
            app_root_dir = self.app_pth.parents[len(self.app_pth.parts) - idx - 1]
        elif 'tests' in self.app_pth.parts:
            idx = self.app_pth.parts.index('tests')
            app_root_dir = self.app_pth.parents[len(self.app_pth.parts) - idx - 1]
        elif 'site-packages' in self.app_pth.parts:
            app_root_dir = self.app_pth.parents[0]
        else:
            for i, part in enumerate(self.app_pth.parts[:-1]):
                if part.lower() == self.app_pth.parts[i + 1].lower():
                    app_root_dir = self.app_pth.parents[len(self.app_pth.parents) - i - 1]
                    break
        return app_root_dir

    def make_archive(self):
        if self.is_dev_mode() and self.app_root_dir:
            self.arc_dir = self.app_root_dir / self.version_archive
            if not self.arc_dir.is_dir():
                self.arc_dir.mkdir()
            self.arc_pth = self.arc_dir / '{} {} ({} Beta).zip'.format(
                self.app_name,
                self.start_date_str,
                self.app_ver
            )
            with zipfile.ZipFile(self.arc_pth, 'w') as archive_zip:
                for ext in self.arc_incl_ext:
                    files = self.app_root_dir.glob('**/*.{}'.format(ext))
                    for file in files:
                        exclude_file = False
                        for excl_dir in self.arc_excl_dir:
                            if excl_dir in file.parts:
                                exclude_file = True
                        if not exclude_file:
                            archive_zip.write(file)
                            pass
            pass

    def make_archive_external(self):
        if self.is_dev_mode() and self.arc_extern_dir:
            if not self.arc_extern_dir.exists():
                self.arc_extern_dir.mkdir()
            shutil.copy(self.arc_pth, self.arc_extern_dir)

    def print_footer(self):
        '''Print standard footers

        Parameters
        ----------

        Returns
        -------
        None

        Examples
        --------

        '''
        success = True
        self.end_time = datetime.datetime.now()
        self.elapsed_time = self.end_time - self.start_time
        self.dur_hours = int(self.elapsed_time.seconds / 3600)
        self.dur_min = int((self.elapsed_time.seconds - self.dur_hours * 3600) / 60)
        self.dur_sec = int(
            self.elapsed_time.seconds - self.dur_hours * 3600 - self.dur_min * 60
        )
        print_str = '\n{:<15}{:<15}'.format(
            'Start:', self.start_time.strftime('%m/%d %H:%M:%S')
        )
        print(print_str)
        print_str = '{:<15}{:<15}'.format(
            'End:', self.end_time.strftime('%m/%d %H:%M:%S')
        )
        print(print_str)
        print_str = '{:<15}{:>5} {:0>2}:{:0>2}:{:0>2}'.format(
            'Duration:',
            self.elapsed_time.days,
            self.dur_hours,
            self.dur_min,
            self.dur_sec,
        )
        print(print_str)
        return success

    def print_header(self, p_cls=True):
        '''Initialize the start of the module, make backup and print standard headers

        Parameters
        ----------
        p_cls
            Clear the screen

        Returns
        -------
        None

        Examples
        --------

        '''
        success = True
        self.cls = p_cls
        if sys.platform.startswith('win32') and self.cls:
            os.system('cls')
        elif sys.platform.startswith('linux') and self.cls:
            os.system('clear')
        args = sys.argv[1:]
        for i, arg in enumerate(args):
            if arg == '-c':
                args[i + 1] = str(self.app_ini_file_name)
        print(
            msg_header(
                '{} ({}) {}\nDescription: {}\n'.format(
                    self.app_name, self.app_ver, ' '.join(args), self.app_desc
                )
            )
        )
        return success


# Message defaults
BAR_LEN = 50
MSG_LEN = 50
CRASH_RETRY = 2


def _add_parm(def_parm, new_parm):
    if isinstance(new_parm, list):
        def_parm += [x for x in new_parm if x not in def_parm]
    elif isinstance(new_parm, str) and new_parm not in def_parm:
        def_parm.append(new_parm)
    return def_parm


def msg_display(p_msg, p_len=MSG_LEN, p_color='white') -> str:
    '''Return a text message in white on black.

    Parameters
    ----------
    p_msg
        The message
    p_len
        The fixed length of the message. Default is beetools.MSG_LEN
    p_color
        Color of text, always on black.
            [ grey, red, green, yellow, blue, magenta, cyan, white ]

    Returns
    -------
    str
        Text in the specified color.

    Examples
    --------
    >>> from beetools import msg.display
    >>> msg.display( 'Display message' )
    '\\x1b[37mDisplay message                               '

    '''
    msg = colored('{: <{len}}'.format(p_msg, len=p_len), p_color)
    return msg[:p_len] + ' '


def msg_error(p_msg) -> str:
    '''Return an "error" text message in red on black

    Parameters
    ----------
    p_msg
        The message

    Returns
    -------
    str
        Text in red on black.

    Examples
    --------
    >>> from beetools import msg.error
    >>> msg.error( 'Error message' )
    '\\x1b[31mError message\\x1b[0m'

    '''
    return colored('{}'.format(p_msg), 'red')


def msg_header(p_msg) -> str:
    '''Return a "header" text message in cyan on black

    Parameters
    ----------
    p_msg
        The message

    Returns
    -------
    str
        Text in red on black.

    Examples
    --------
    >>> from beetools import msg.header
    >>> msg.header( 'Header message' )
    '\\x1b[36mHeader message\\x1b[0m'

    '''
    return colored('{}'.format(p_msg), 'cyan')


def msg_info(p_msg) -> str:
    '''Return an "information" text message in yellow on black

    Parameters
    ----------
    p_msg
        The message

    Returns
    -------
    str
        Text in red on black.

    Examples
    --------
    >>> from beetools import msg.info
    >>> msg.info( 'Info message' )
    '\\x1b[33mInfo message\\x1b[0m'

    '''
    return colored('{}'.format(p_msg), 'yellow')


def msg_milestone(p_msg) -> str:
    '''Return a "milestone" text message in magenta on black

    Parameters
    ----------
    p_msg
        The message

    Returns
    -------
    str
        Text in red on black.

    Examples
    --------
    >>> from beetools import msg.milestone
    >>> msg.milestone( 'Milestone message' )
    '\\x1b[35mMilestone message\\x1b[0m'

    '''
    return colored('{}'.format(p_msg), 'magenta')


def msg_ok(p_msg) -> str:
    '''Return an "OK" text message in green on black

    Parameters
    ----------
    p_msg
        The message

    Returns
    -------
    str
        Text in red on black.

    Examples
    --------
    >>> from beetools import msg.ok
    >>> msg.ok( 'OK message' )
    '\\x1b[32mOK message\\x1b[0m'

    '''
    return colored('{}'.format(p_msg), 'green')


def example_archiver(p_cls=True):
    '''Example to illustrate usage

    Parameters
    ----------
    p_cls
        Clear the screen before start
        Default is True

    Returns
    -------
    bool
        Successful execution [ b_tls.arc_pth | False ]

    Examples
    --------

    '''

    success = True
    app_name = 'TestApp'
    app_version = '0.0.1'
    app_desc = 'Test application description'
    with tempfile.TemporaryDirectory() as temp_dir:
        app_dir = Path(temp_dir, app_name, 'src', app_name.lower())
        app_dir.mkdir(parents = True)
        app_pth = app_dir / Path(app_name.lower()).with_suffix('.py')
        app_pth.touch()
        arc_extern_dir = Path(temp_dir, 'external')
        # arc_extern_dir.mkdir(parents = True)
        t_archiver = Archiver(app_name, app_version, app_desc, app_pth, p_arc_extern_dir = arc_extern_dir)
    t_archiver.print_header(p_cls = p_cls)
    t_archiver.print_footer()
    # working_dir.rmdir()
    return success


def example_messaging():
    '''Standard example to illustrate standard use.

    Parameters
    ----------

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_path | False ]

    Examples
    --------

    '''
    success = True
    print(
        msg_display(
            'This message print in blue and cut at {} character because it is too long!'.format(
                MSG_LEN),
            p_color = 'blue'
        )
    )
    print(msg_ok('This message is an OK message'))
    print(msg_info('This is an info message'))
    print(msg_milestone('This is a milestone message'))
    print(msg_error('This is a warning message'))
    return success


def do_examples(p_cls = True):
    success = True
    success = example_archiver(p_cls = p_cls) and success
    success = example_messaging() and success
    return success


if __name__ == '__main__':
    do_examples()
