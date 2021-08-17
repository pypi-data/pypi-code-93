
'''Tools for Bright Edge eServices developments & projects

These tools was designed for the use in the Bright Edge eServices echo system.
It defines methods and functions for general use purposes and standardization
in the Bright Edge eServices echo system.

The module define defaults for log levels, display on console, operating
system names and date formats.

The defaults are used in this module and across the Bright Edge eServices
echo system.  The module basically has

To Do
=====
1.  Better example on the logging integration
2.  Complete doctests for all methods & functions

'''

import datetime
import logging
import os
import zipfile
from pathlib import Path
import shutil
import sys
import tempfile
from beetools.msg import header as msg_header

_PROJ_DESC = __doc__.split('\n')[0]
_PROJ_PATH = Path(__file__)
_PROJ_NAME = _PROJ_PATH.stem
_PROJ_VERSION = '3.2.0'


class Archiver:
    '''Create an instance keep meta data about an application and backup
    specified files to a zipfile during development.

    Archiver assume the following project structure of the caling application:

    Module
    ======
    projectname/ (a.k.a Project base folder)
    │
    ├── Data/
    │
    ├── docs/
    │
    ├── src/ (a.k.a Srouce folder)
    │   └── modname (a.k.a Project folder
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
    projectname/ (a.k.a Project base folder)
    │
    ├── Data/
    │
    ├── docs/
    │
    ├── pkgname/ (a.k.a Project folder
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

    Library (not implimented)
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
        p_archive_ext = None
    ):
        '''Initialize the object

        Parameters
        ----------
        p_parent_log_name
            Name of the parent logger i.e. calling application
        p_app_ver
            Version of the calling application
        p_app_desc
            Description of the calling application
        p_app_pth
            Path to the application module
        p_app_ini_file_name
            Ini file name used by calling application for paramenters
            Default is None
        p_cls
            Clear the screen before start
            Default is True

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

        if not isinstance(p_app_pth, Path):
            self.app_pth = Path(p_app_pth)
        else:
            self.app_pth = p_app_pth
        self.app_base_dir = self.find_app_base_dir()
        self.app_desc = p_app_desc
        self.app_ini_file_name = p_app_ini_file_name
        self.app_name = self.app_pth.stem
        self.app_ver = p_app_ver
        self.archive_dir = None
        if p_archive_ext is None:
            self.archive_ext = ['ini', 'py']
        else:
            self.archive_ext = p_archive_ext
        self.archive_pth = None
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
        pass

    def is_dev_mode(self):
        '''Determine if module is in production or not

        Parameters
        ----------

        Returns
        -------

        Examples
        --------

        '''
        if 'site-packages' not in self.app_pth.parts:
            return True
        return False

    def find_app_base_dir(self):
        app_base_dir = None
        if self.is_dev_mode():
            if 'src' in self.app_pth.parts:
                idx = self.app_pth.parts.index('src')
                app_base_dir = self.app_pth.parents[len(self.app_pth.parts) - idx - 1]
            elif 'tests' in self.app_pth.parts:
                idx = self.app_pth.parts.index('tests')
                app_base_dir = self.app_pth.parents[len(self.app_pth.parts) - idx - 1]
            elif self.app_name.lower() in self.app_pth.parts:
                idx = self.app_pth.parts.index(self.app_name.lower())
                if self.app_pth.parts[idx + 1] == self.app_name.lower():
                    app_base_dir = self.app_pth.parents[len(self.app_pth.parts) - idx - 1]
        return app_base_dir

    def make_archive(self):
        if self.is_dev_mode() and self.app_base_dir:
            self.archive_dir = self.app_base_dir / self.version_archive
            if not self.archive_dir.is_dir():
                self.archive_dir.mkdir()
            self.archive_pth = self.archive_dir / '{} {} ({} Beta).zip'.format(
                self.app_name,
                self.start_date_str,
                self.app_ver
            )
            with zipfile.ZipFile( self.archive_pth, 'w') as archive_zip:
                for ext in self.archive_ext:
                    files = self.app_base_dir.glob('**/*.{}'.format(ext))
                    for file in files:
                        if self.version_archive not in Path(file).parts:
                            archive_zip.write(file)

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
        '''Initialize the start of the module,. make backup and print standard headers

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


def do_examples(p_cls=True):
    '''Example to illustrate usage

    Parameters
    ----------
    p_cls
        Clear the screen before start
        Default is True

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_pth | False ]

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
        t_archiver = Archiver(app_name, app_version, app_desc, app_pth)
    t_archiver.print_header(p_cls = p_cls)
    t_archiver.print_footer()
    # working_dir.rmdir()
    if success:
        return t_archiver.archive_pth
    return False


if __name__ == '__main__':
    # do_examples(sys.argv[0])
    do_examples()
