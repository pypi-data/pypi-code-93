
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

import configparser
import datetime
import inspect
import logging
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from termcolor import colored

_path = Path(__file__)
_name = _path.stem
_VERSION = '3.2.0'

# Default logging constants
DEF_LOG_LEV = logging.DEBUG
DEF_LOG_LEV_FILE = logging.DEBUG
DEF_LOG_LEV_CON = logging.WARNING
LOG_FILE_NAME = Path(sys.argv[0]).parent / '{}.{}'.format(Path(sys.argv[0]).stem, 'log')
LOG_FILE_FORMAT = '%(asctime)s%(msecs)d;%(levelname)s;%(name)s;%(funcName)s;%(message)s'
LOG_CONSOLE_FORMAT = (
    '\x1b[0;31;40m\n%(levelname)s - %(name)s - %(funcName)s - %(message)s\x1b[0m'
)

# Default date format strings
LOG_DATE_FORMAT = '%Y%m%d%H%M%S'
LONG_DATE_FORMAT = '%Y%m%d'
TIME_FORMAT = '%H%M%S'

# Message defaults
BAR_LEN = 50
MSG_LEN = 50
CRASH_RETRY = 2

# Operating system name defaults
WINDOWS = 'windows'
LINUX = 'linux'
MACOS = 'macos'
AIX = 'aix'

# Codec List Updated 2021/06/29
CODEC_LIST = [
    ['ascii', '646, us-ascii', 'English'],
    ['big5', 'big5-tw, csbig5', 'Traditional Chinese'],
    ['big5hkscs', 'big5-hkscs, hkscs', 'Traditional Chinese'],
    ['cp037', 'IBM037, IBM039', 'English'],
    ['cp273', '273, IBM273, csIBM273', 'German New in version 3.4.'],
    ['cp424', 'EBCDIC-CP-HE, IBM424', 'Hebrew'],
    ['cp437', '437, IBM437', 'English'],
    ['cp500', 'EBCDIC-CP-BE, EBCDIC-CP-CH, IBM500', 'Western Europe'],
    ['cp720', 'Arabic', 'cp737', 'Greek'],
    ['cp775', 'IBM775', 'Baltic languages'],
    ['cp850', '850, IBM850', 'Western Europe'],
    ['cp852', '852, IBM852', 'Central and Eastern Europe'],
    ['p855', '855, IBM855', 'Bulgarian, Byelorussian, Macedonian, Russian, Serbian'],
    ['cp856', 'Hebrew'],
    ['cp857', '857, IBM857', 'Turkish'],
    ['cp858', '858, IBM858', 'Western Europe'],
    ['cp860', '860, IBM860', 'Portuguese'],
    ['cp861', '861, CP-IS, IBM861', 'Icelandic'],
    ['cp862', '862, IBM862', 'Hebrew'],
    ['cp863', '863, IBM863', 'Canadian'],
    ['cp864', 'IBM864', 'Arabic'],
    ['cp865', '865, IBM865', 'Danish, Norwegian'],
    ['cp866', '866, IBM866', 'Russian'],
    ['cp869', '869, CP-GR, IBM869', 'Greek'],
    ['cp874', 'Thai'],
    ['cp875', 'Greek'],
    ['cp932', '932, ms932, mskanji, ms-kanji', 'Japanese'],
    ['cp949', '949, ms949, uhc', 'Korean'],
    ['cp950', '950, ms950;Traditional Chinese'],
    ['cp1006', 'Urdu'],
    ['cp1026', 'ibm1026', 'Turkish'],
    ['cp1125', '1125, ibm1125, cp866u, ruscii', 'Ukrainian New in version 3.4.'],
    ['cp1140', 'ibm1140', 'Western Europe'],
    ['cp1250', 'windows-1250', 'Central and Eastern Europe'],
    ['cp1251', 'windows-1251', 'Bulgarian, Byelorussian, Macedonian, Russian, Serbian'],
    ['cp1252', 'windows-1252', 'Western Europe'],
    ['cp1253', 'windows-1253', 'Greek'],
    ['cp1254', 'windows-1254', 'Turkish'],
    ['cp1255', 'windows-1255', 'Hebrew'],
    ['cp1256', 'windows-1256', 'Arabic'],
    ['cp1257', 'windows-1257', 'Baltic languages'],
    ['cp1258', 'windows-1258', 'Vietnamese'],
    ['euc_jp', 'eucjp, ujis, u-jis', 'Japanese'],
    ['euc_jis_2004', 'jisx0213, eucjis2004', 'Japanese'],
    ['euc_jisx0213', 'eucjisx0213', 'Japanese'],
    [
        'euc_kr',
        'euckr, korean, ksc5601, ks_c-5601, ks_c-5601-1987, ksx1001, ks_x-1001',
        'Korean',
    ],
    [
        'gb2312',
        'chinese, csiso58gb231280, euc-cn, euccn, eucgb2312-cn, gb2312-1980, gb2312-80, iso-ir-58',
        'Simplified Chinese',
    ],
    ['gbk', '936, cp936, ms936', 'Unified Chinese'],
    ['gb18030', 'gb18030-2000', 'Unified Chinese'],
    ['hz', 'hzgb, hz-gb, hz-gb-2312', 'Simplified Chinese'],
    ['iso2022_jp', 'csiso2022jp, iso2022jp, iso-2022-jp', 'Japanese'],
    ['iso2022_jp_1', 'iso2022jp-1, iso-2022-jp-1', 'Japanese'],
    [
        'iso2022_jp_2',
        'iso2022jp-2, iso-2022-jp-2',
        'Japanese, Korean, Simplified Chinese, Western Europe, Greek',
    ],
    ['iso2022_jp_2004', 'iso2022jp-2004, iso-2022-jp-2004', 'Japanese'],
    ['iso2022_jp_3', 'iso2022jp-3, iso-2022-jp-3', 'Japanese'],
    ['iso2022_jp_ext', 'iso2022jp-ext, iso-2022-jp-ext', 'Japanese'],
    ['iso2022_kr', 'csiso2022kr, iso2022kr, iso-2022-kr', 'Korean'],
    [
        'latin_1',
        'iso-8859-1, iso8859-1, 8859, cp819, latin, latin1, L1',
        'Western Europe',
    ],
    ['iso8859_2', 'iso-8859-2, latin2, L2', 'Central and Eastern Europe'],
    ['iso8859_3', 'iso-8859-3, latin3, L3', 'Esperanto, Maltese'],
    ['iso8859_4', 'iso-8859-4, latin4, L4', 'Baltic languages'],
    [
        'iso8859_5',
        'iso-8859-5, cyrillic',
        'Bulgarian, Byelorussian, Macedonian, Russian, Serbian',
    ],
    ['iso8859_6', 'iso-8859-6, arabic', 'Arabic'],
    ['iso8859_7', 'iso-8859-7, greek, greek8', 'Greek'],
    ['iso8859_8', 'iso-8859-8, hebrew', 'Hebrew'],
    ['iso8859_9', 'iso-8859-9, latin5, L5', 'Turkish'],
    ['iso8859_10', 'iso-8859-10, latin6, L6', 'Nordic languages'],
    ['iso8859_11', 'iso-8859-11, thai', 'Thai languages'],
    ['iso8859_13', 'iso-8859-13, latin7, L7', 'Baltic languages'],
    ['iso8859_14', 'iso-8859-14, latin8, L8', 'Celtic languages'],
    ['iso8859_15', 'iso-8859-15, latin9, L9', 'Western Europe'],
    ['iso8859_16', 'iso-8859-16, latin10, L10', 'South-Eastern Europe'],
    ['johab', 'cp1361, ms1361', 'Korean'],
    ['koi8_r', 'Russian'],
    ['koi8_t', 'Tajik New in version 3.5.'],
    ['koi8_u', 'Ukrainian'],
    ['kz1048', 'kz_1048, strk1048_2002, rk1048', 'Kazakh New in version 3.5.'],
    [
        'mac_cyrillic',
        'maccyrillic',
        'Bulgarian, Byelorussian, Macedonian, Russian, Serbian',
    ],
    ['mac_greek', 'macgreek', 'Greek'],
    ['mac_iceland', 'macicelandIcelandic'],
    [
        'mac_latin2',
        'maclatin2, maccentraleurope, mac_centeuro',
        'Central and Eastern Europe',
    ],
    ['mac_roman', 'macroman, macintosh', 'Western Europe'],
    ['mac_turkish', 'macturkish', 'Turkish'],
    ['ptcp154', 'csptcp154, pt154, cp154, cyrillic-asian', 'Kazakh'],
    ['shift_jis', 'csshiftjis, shiftjis, sjis, s_jis', 'Japanese'],
    ['shift_jis_2004', 'shiftjis2004, sjis_2004, sjis2004', 'Japanese'],
    ['shift_jisx0213', 'shiftjisx0213, sjisx0213, s_jisx0213', 'Japanese'],
    ['utf_32', 'U32, utf32', 'all languages'],
    ['utf_32_be', 'UTF-32BE', 'all languages'],
    ['utf_32_le', 'UTF-32LE', 'all languages'],
    ['utf_16', 'U16, utf16', 'all languages'],
    ['utf_16_be', 'UTF-16BE', 'all languages'],
    ['utf_16_le', 'UTF-16LE', 'all languages'],
    ['utf_7', 'U7, unicode-1-1-utf-7', 'all languages'],
    ['utf_8', 'U8, UTF, utf8, cp65001', 'all languages'],
    ['utf_8_sig', '', 'all languages'],
]


def activate_venv_cmd(p_venv_base_fldr, p_venv_name) -> str:
    '''Compile command to activate a virtual environment

    This method is useful in the exec_batch_in_session() method to invoke a virtual
    environment in a session to execute other commands in the virtual
    environment.

    Parameters
    ----------
    p_venv_base_fldr
        This is the "root" folder of the virtual environment will be
        creates in
    p_venv_name
        The name of the virtual environment.

    Returns
    -------
    str
        The command to activate the virtual environment depending on the
        operating system.

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    activate_venv_cmd(get_tmp_fldr(),'new-project')
    'source /tmp/new-project_env/bin/activate'

    '''
    if get_os() in [LINUX, MACOS]:
        cmd = 'source {}'.format(
            get_venv_fldr(p_venv_base_fldr, p_venv_name) / Path('bin', 'activate')
        )
    elif get_os() == WINDOWS:
        cmd = 'CALL {}'.format(
            get_venv_fldr(p_venv_base_fldr, p_venv_name) / Path('Scripts', 'activate')
        )
    return cmd


def exec_batch_in_session(
    p_script_cmds,
    p_switches=None,
    p_crash=True,
    p_script_name=False,
    p_verbose=False,
    p_shell=False,
) -> subprocess.CompletedProcess:
    '''Execute a script in the same session

    Useful when commands has to be exucuted in one session for instance if
    it a a virtual environment is envoked and the commands must be executed
    in the virtual environment.

    Parameters
    ----------
    p_script_cmds
        Commands to execute in a list
    p_switches
        Switches for the bash script.
        Default is None.
    p_crash
        Stop (crash) or continue execution should a command fail.
        Default is True
    p_script_name
        Name of the script to use
        Default is False and will be set to "do_bashs_cript_temp"
    p_verbose
        Give feedback (or not)
        Default is False
    p_shell
        Run the script in a shell.  See https://docs.python.org/3.9/library/subprocess.html#subprocess.run
        Default is False

    Returns
    -------
    subprocess.CompletedProcess
        See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    tmp_test = get_tmp_fldr() / 'test'
    tmp_t1 = tmp_test / 't1'
    cmd = ['mkdir -p {}'.format(tmp_t1), 'ls -l {}'.format(tmp_test), 'rm -R {}'.format(tmp_test)]
    exec_batch_in_session(cmd)
    '''
    if isinstance(p_switches, list):
        switches = p_switches
    elif isinstance(p_switches, str):
        switches = list(shlex.shlex(p_switches))
    else:
        switches = []
    if get_os() in [LINUX, MACOS]:
        script = ['bash'] + switches
        ext = 'sh'
        contents = '#!/bin/bash\n'
    elif get_os() == WINDOWS:
        script = []
        ext = 'bat'
        contents = ''
    else:
        print(colored('Unknown OS ({})\nSystem terminated!'.format(get_os()), 'red'))
        sys.exit()

    if not p_script_name:
        p_script_name = 'exec_batch_in_session_temp'
    batch_pth = get_tmp_fldr() / Path('{}.{}'.format(p_script_name, ext))
    script.append(str(batch_pth))
    contents = write_script(batch_pth, p_script_cmds)
    if get_os() == MACOS:
        batch_pth.chmod(0o777)
    if p_verbose:
        print(
            msg_info(
                '==[Start {0}]====\n{1}==[ End {0} ]===='.format(batch_pth, contents)
            )
        )
    compl_proc = exec_cmd(script, p_crash, p_verbose=p_verbose, p_shell=p_shell)
    if os.path.isfile(batch_pth):
        os.remove(batch_pth)
        pass
    return compl_proc


def exec_batch(p_batch, p_verbose=False) -> bool:
    '''Execute a batch.

    Each command will be executed independantly of the previous one i.e it
    will be in a different session.
    Parameters
    ----------
    p_cmd
        Command to execute.  See See https://docs.python.org/3.9/library/subprocess.html#subprocess.run
    p_crash
        Stop (crash) or continue execution should a command fail.
    p_shell
        Run the script in a shell.  See https://docs.python.org/3.9/library/subprocess.html#subprocess.run
        Default is None
    p_verbose
        Give feedback (or not)
        Default is False

    Returns
    -------
    bool
        If successful it returns True (subprocess.CompletedProcess = 0)
        alternatively it returns a subprocess.CompletedProcess
        See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    >>> from beetools import exec_batch
    >>> exec_batch([[ 'echo', 'Hello'],['echo','Goodbye']])
    True

    '''
    success = True
    # c_cmd = 1
    for cmd in p_batch:
        rc = exec_cmd(cmd, p_verbose=p_verbose)
        if rc is not True:
            success = success and False
    return success


def exec_cmd(p_cmd, p_crash=True, p_shell=None, p_verbose=False) -> bool:
    '''Execute a command line instruction on Linux or Windows

    Parameters
    ----------
    p_cmd
        Command to execute.  See See https://docs.python.org/3.9/library/subprocess.html#subprocess.run
    p_crash
        Stop (crash) or continue execution should a command fail.
    p_shell
        Run the script in a shell.  See https://docs.python.org/3.9/library/subprocess.html#subprocess.run
        Default is None
    p_verbose
        Give feedback (or not)
        Default is False

    Returns
    -------
    bool
        If successful it returns True (subprocess.CompletedProcess = 0)
        alternatively it returns a subprocess.CompletedProcess
        See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    >>> from beetools import exec_cmd
    >>> exec_cmd([ 'echo', 'Hello'])
    True

    '''
    success = True
    p_cmd = [str(s) for s in p_cmd]
    inst_str = ' '.join(p_cmd)
    if p_verbose:
        print(msg_info('{}'.format(inst_str)))
    if get_os() in [LINUX, MACOS] and not p_shell:
        shell = False
    elif get_os() == WINDOWS and not p_shell:
        shell = True
    elif get_os() not in [WINDOWS, LINUX, MACOS]:
        print(colored('Unknow OS ({})\nSystem terminated!'.format(get_os()), 'red'))
        sys.exit()
    else:
        shell = p_shell
    try:
        comp_proc = subprocess.run(
            p_cmd, capture_output=False, shell=shell, check=False
        )
        comp_proc.check_returncode()
    except subprocess.CalledProcessError:
        print('\nCmd:\t{}\nrc:\t{}'.format(inst_str, comp_proc.returncode))
        if p_crash:
            print(colored('System terminated!', 'red'))
            sys.exit()
        else:
            print('Crash = False.  Execution will continue...')
    if comp_proc.returncode != 0:
        success = comp_proc.returncode
    return success


def get_os() -> str:
    '''Return a constant for the current operating system

    Parameters
    ----------
    None

    Returns
    -------
    str
        "linux" | "windows"

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    get_os()
    'linux'
    '''
    if sys.platform.startswith('win32'):
        curr_os = WINDOWS
    elif sys.platform.startswith('linux'):
        curr_os = LINUX
    elif sys.platform.startswith('darwin'):
        curr_os = MACOS
    elif sys.platform.startswith('aix'):
        curr_os = AIX
    else:
        print('OS not listed\nSystem will now ternminate')
        sys.exit()
    return curr_os


def get_tmp_fldr() -> Path:
    '''Return os related temporary folder for user.

    Parameters
    ----------
    None

    Returns
    -------
    Path
        Path object with temp folder for user and os

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    get_tmp_fldr()
    PosixPath('/tmp')

    '''
    if get_os() == LINUX:
        temp = '/tmp'
    elif get_os() == WINDOWS:
        temp = os.environ['TEMP']
    elif get_os() == MACOS:
        temp = os.environ['TMPDIR']
    return Path(temp)


def get_venv_fldr(p_venv_base_fldr, p_name_pref) -> Path:
    '''Compile the virtual environment base folder in Bright Edge eServices format

    Parameters
    ----------
    p_venv_base_fldr
        This is the "root" folder of the virtual environment will be
        creates in
    p_venv_name
        The name of the virtual environment.

    Returns
    -------
    Path
        Path object with virtual environment name

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    beetools.get_venv_fldr(beetools.get_tmp_fldr(), 'new-project')
    PosixPath('/tmp/new-project_env')

    '''
    return p_venv_base_fldr / Path('{}_env'.format(p_name_pref))


def install_in_venv(p_venv_base_fldr, p_venv_name, p_instructions, p_verbose=True):
    '''Execute (install) commands in a virtual environment

    Parameters
    ----------
    p_venv_base_fldr
        This is the "root" folder of the virtual environment will be
        creates in
    p_venv_name
        The name of the virtual environment.
    p_instructions
        Instructions to execute in virtual environment
    p_verbose
        Give feedback (or not)
        Default is True

    Returns
    -------
    subprocess.CompletedProcess
    See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    beetools.install_in_venv( beetools.get_tmp_fldr(),
                              'new-project',
                              ['echo Installing in VEnv','pip install wheel','echo Done!'])
    + sudo -i
    Installing in VEnv
    Done!
    + exit
    True

    '''
    switches = []
    script_name = 'install_in_venv'
    if get_os() == LINUX:
        switches = ['-x']
        script_cmds = ['sudo -i << _EOF_']
    elif get_os() == WINDOWS:
        script_cmds = []
        if p_verbose:
            script_cmds.append('@ECHO OFF')
    elif get_os() == MACOS:
        script_cmds = []
        if p_verbose:
            script_cmds.append('@ECHO OFF')
    script_cmds.append('{}\n'.format(activate_venv_cmd(p_venv_base_fldr, p_venv_name)))
    for instr in p_instructions:
        script_cmds.append(instr)
    if get_os() == LINUX:
        script_cmds.append('_EOF_')
        script_cmds.append('exit')
    ret_code = exec_batch_in_session(
        script_cmds, p_script_name=script_name, p_verbose=p_verbose, p_switches=switches
    )
    return ret_code


def is_struct_the_same(p_x, p_y, p_ref='') -> bool:
    '''Compare two structures

    Parameters
    ----------
    p_x
        "Left" structure
    p_y
        "Right" structure
    p_ref
        Reference string
        Default is ''

    Returns
    -------
    bool
        True is structure are the same.  If the contents of dictionaries are the same
        but not necessarily in the same order, the are still regarded as "the same".

    Examples
    --------
    >>> x=[1,2]
    >>> y=[1,2]
    >>> from beetools import is_struct_the_same
    >>> is_struct_the_same(x,y)
    True

    >>> x={1:'One',2:'Two'}
    >>> y={2:'Two',1:'One'}
    >>> from beetools import is_struct_the_same
    >>> is_struct_the_same(x,y)
    True

    >>> z={2:'Two',1:'Three'}
    >>> from beetools import is_struct_the_same
    >>> is_struct_the_same(y,z,'ref str')
    ref str.1.One
    <>
    ref str.1.Three
    False
    '''
    success = True
    x_len = 0
    y_len = 0
    if isinstance(p_x, (dict, list, tuple)):
        x_len = len(p_x)
        y_len = len(p_y)
    if x_len == y_len:
        if isinstance(p_x, dict) and isinstance(p_y, dict):
            x_keys_srt = sorted(p_x.keys())
            y_keys_srt = sorted(p_y.keys())
            for key in x_keys_srt:
                if key in y_keys_srt:
                    ref = '{}.{}'.format(p_ref, key)
                    success = is_struct_the_same(p_x[key], p_y[key], ref) and success
                else:
                    print('Key {}[ {} ] not in both structures'.format(p_ref, key))
                    success = False
        elif (isinstance(p_x, list) and isinstance(p_y, list)) or (
            isinstance(p_x, tuple) and isinstance(p_y, tuple)
        ):
            for i, rec in enumerate(p_x):
                ref = '{}[ {} ]'.format(p_ref, i)
                success = is_struct_the_same(rec, p_y[i], p_ref) and success
        elif p_x != p_y:
            print('{0}.{1}\n<>\n{0}.{2}'.format(p_ref, p_x, p_y))
            success = False
    else:
        print(
            'Length of items in structure differ:\n{}\nx({}) = {}\ny({}) = {}'.format(
                p_ref, x_len, p_x, y_len, p_y
            )
        )
        success = False
    return success


def msg_display(p_msg, p_len=MSG_LEN, p_color='white') -> str:
    '''Return a text message in white on black

    Parameters
    ----------
    p_msg
        The message
    p_len
        The fixed length of the message.  Default is beetools.MSG_LEN
    p_color
        Color of text, always on black.
            [ grey, red, green, yellow, blue, magenta, cyan, white ]

    Returns
    -------
    str
        Text in the specified color.

    Examples
    --------
    >>> from beetools import msg_display
    >>> msg_display( 'Display message' )
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
    >>> from beetools import msg_error
    >>> msg_error( 'Error message' )
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
    >>> from beetools import msg_header
    >>> msg_header( 'Header message' )
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
    >>> from beetools import msg_info
    >>> msg_info( 'Info message' )
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
    >>> from beetools import msg_milestone
    >>> msg_milestone( 'Milestone message' )
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
    >>> from beetools import msg_ok
    >>> msg_ok( 'OK message' )
    '\\x1b[32mOK message\\x1b[0m'

    '''
    return colored('{}'.format(p_msg), 'green')


def result_rep(p_success, p_comment='No Comment') -> str:
    '''Print a formatted result report

    Parameters
    ----------
    p_success
        True | False
    p_comment
        Comment to print
        Default is "No Comment"

    Returns
    -------
    str
        Formatted result text

    Examples
    --------
    >>> from beetools import result_rep
    >>> result_rep(True)
    <module> - \x1b[32mSuccess\x1b[0m (No Comment)
    '<module> - \\x1b[32mSuccess\\x1b[0m (No Comment)'
    '''
    proc_name = inspect.getouterframes(inspect.currentframe(), 1)[1][3]
    if p_success:
        ret_str = '{} - {} ({})'.format(proc_name, msg_ok('Success'), p_comment)
    else:
        ret_str = '{} - {} ({})'.format(proc_name, msg_error('Failed'), p_comment)
    print(ret_str)
    return ret_str


def rm_locked_file(p_file_path) -> bool:
    '''Attempt to remove a temporary locked file

    Parameters
    ----------
    p_file_path
        Patch object

    Returns
    -------
    None

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent

    '''
    crash_retry_cntr = 0
    success = False
    while crash_retry_cntr < CRASH_RETRY:
        try:
            if p_file_path.is_file():
                p_file_path.unlink()
            if p_file_path.is_dir():
                shutil.rmtree(p_file_path)
            success = True
        except shutil.Error:
            crash_retry_cntr += 1
        else:
            crash_retry_cntr = CRASH_RETRY
    return success


def rm_tree(p_pth, p_crash=True):
    '''Remove a tree structure

    Parameters
    ----------
    p_pth
        Root f the tree to remove
    p_crash
        If true, the system will terminate if the structure can not be removed

    Returns
    -------
    Bool
        Status of the operation

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent

    '''
    success = False
    tree = list(p_pth.glob('**/*'))
    not_empty = []
    while len(tree) > 0:
        for src in tree:
            if src.is_file():
                src.unlink()
            elif src.is_dir():
                try:
                    src.rmdir()
                except OSError:
                    if src.exists():
                        not_empty.append(src)
        tree = not_empty.copy()
        not_empty = []
    if p_pth.exists():
        try:
            p_pth.rmdir()
            success = True
        except OSError:
            if p_crash:
                print(msg_error('{} could not be removed.\nSystem terminated.'))
                sys.exit()
            else:
                print(msg_error('{} could not be removed.\nExcecution will continue.'))
    return success


def select_os_fldr_from_config(p_config, p_section, p_option) -> Path:
    '''Select the correct folder on a specific os in the Bright Edge eServices
    echo system.

    This is useful when the application runs on different os' and an option
    must be slected dependent on the os and/or the system.  Folders or directories
    are the usual culprits.

    Parameters
    ----------
    p_config
        ConfigParser object.
        See https://docs.python.org/3.9/library/configparser.html#module-configparser
    p_section
        Section to inspect
    p_option
        Option to find for the operating system

    Returns
    -------
    Path
        Path object for the correct folder for the operating system.

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    cnf = configparser.ConfigParser()
    cnf.read_dict({ 'Folders' :
                    { 'windows1_MyFolderOnSystem' : 'c:\\Program Files',
                      'windows2_MyFolderOnSystem' : 'c:\\Program Files (x86)',
                      'linux1_MyFolderOnSystem'   : '/usr/local/bin',
                      'linux2_MyFolderOnSystem'   : '/bin'}})
    select_os_fldr_from_config( cnf, 'Folders', 'MyFolderOnSystem' )
    beetools.select_os_fldr_from_config( cnf, 'Folders', 'MyFolderOnSystem' )
    PosixPath('/usr/local/bin')

    '''
    options = p_config.options(p_section)
    fldr = None
    for option in options:
        if (
            option.split('_')[0][:-1] == get_os()
            and option.split('_')[1].lower() == p_option.lower()
        ):
            fldr = Path(p_config.get(p_section, option))
            if not fldr.is_dir():
                fldr = None
            else:
                break
    if not fldr:
        print(
            msg_error(
                'select_os_fldr_from_config not found: {}:{}'.format(
                    p_section, p_option
                )
            )
        )
    return fldr


def set_up_venv(
    p_venv_base_fldr, p_venv_name, p_package_list=None, p_verbose=True
) -> bool:
    '''Create a virtual environment with some defaults

    Parameters
    ----------
    p_venv_base_fldr
        This is the "root" folder of the virtual environment will be
        creates in
    p_venv_name
        The name of the virtual environment.
    p_package_list
        List of packages to install

    Returns
    -------
    subprocess.CompletedProcess
    See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    >>> from beetools import set_up_venv, get_tmp_fldr
    >>> set_up_venv( get_tmp_fldr(),'new-project',['pip','wheel'],p_verbose=False)
    True

    '''
    switches = []
    script_cmds = []
    if get_os() == WINDOWS:
        pip_cmd = 'pip'
    elif get_os() in [LINUX, MACOS]:
        pip_cmd = 'pip3'
        switches = ['-x']
        script_cmds = ['sudo -i << _EOF_']
    exec_cmd(
        [
            'python',
            '-m',
            'venv',
            get_venv_fldr(p_venv_base_fldr, p_venv_name),
        ],
        p_verbose=p_verbose,
    )
    script_name = 'set_up_venv'
    script_cmds.append('{}\n'.format(activate_venv_cmd(p_venv_base_fldr, p_venv_name)))
    if not p_package_list:
        p_package_list = []
    for package in p_package_list:
        if package[0] == 'Web':
            script_cmds.append('{} install {}'.format(pip_cmd, package[1]))
        elif package[0] == 'Local':
            script_cmds.append(
                '{} install --find-links {} {}'.format(pip_cmd, package[2], package[1])
            )
    if get_os() == LINUX:
        script_cmds.append('_EOF_')
        script_cmds.append('exit')
    ret_code = exec_batch_in_session(
        script_cmds, p_script_name=script_name, p_verbose=p_verbose, p_switches=switches
    )
    return ret_code


def write_script(p_pth, p_contents) -> str:
    '''Write a script to disk

    Parameters
    ----------
    p_pth
        Path to the script
    p_contents
        Contents of the script

    Returns
    -------
    subprocess.CompletedProcess
    See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    >>> from beetools import set_up_venv, get_tmp_fldr
    >>> set_up_venv( get_tmp_fldr(),'new-project',['pip','wheel'],p_verbose=False)
    True

    '''
    contents = ''
    for line in p_contents:
        if isinstance(line, list):
            contents += ' '.join(line) + '\n'
        else:
            contents += '{}\n'.format(line)
    p_pth.write_text(contents)
    return contents


class Archiver:
    '''Creat a object to keep meta data and backup certial files in the Bright
    Edge eServices eco system.'''

    def __init__(
        self,
        p_parent_log_name,
        p_app_ver,
        p_app_desc,
        p_app_path,
        p_app_ini_file_name=None,
        p_cls=True,
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
        p_app_path
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
        >>> au = Archiver(__name__, _VERSION, __doc__, p_app_path=Path(__file__))
        >>>

        '''

        self.success = True
        self.log_name = '{}.{}'.format(p_parent_log_name, __name__)
        self.logger = logging.getLogger(self.log_name)
        self.logger.info('Start')
        if not isinstance(p_app_path, Path):
            self.app_path = Path(p_app_path)
        else:
            self.app_path = p_app_path
        self.app_code_fldr = self.app_path.parent
        self.app_desc = p_app_desc
        self.app_ini_file_name = p_app_ini_file_name
        self.app_name = self.app_path.stem
        self.app_ver = p_app_ver
        self.archive_sub_fldr = 'VersionArchive'
        self.cls = p_cls
        self.dur_hours = 0
        self.dur_min = 0
        self.dur_sec = 0
        self.elapsed_time = 0
        self.end_time = 0
        self.start_time = datetime.datetime.now()
        self.start_date_str = self.start_time.strftime('%y%m%d%H%M%S')
        self.version_archive_fldr = self.app_code_fldr / self.archive_sub_fldr
        if not self.version_archive_fldr.is_dir():
            self.version_archive_fldr.mkdir()
        self.archive_path = self.version_archive_fldr / '{} {} ({} Beta).py'.format(
            self.app_name, self.start_date_str, self.app_ver
        )
        shutil.copy(self.app_path, self.archive_path)

    def print_footer(self):
        '''Print standard footers

        Parameters
        ----------
        None

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
        self.dur_min = int(
            (self.elapsed_time.seconds - self.dur_hours * 3600) / 60
        )
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


def example_logging():
    '''Standard example to illustrate logging use.

    Parameters
    ----------
    p_app_path
        Path to the application module
    p_cls
        Clear the screen before start
        Default is True

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_path | False ]

    Examples
    --------

    '''
    success = True
    # Set-up loggers to console and file with different log levels.
    logger = logging.getLogger(__name__)
    logger.setLevel(DEF_LOG_LEV)
    file_handler = logging.FileHandler(LOG_FILE_NAME, mode='w')
    file_handler.setLevel(DEF_LOG_LEV_FILE)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(DEF_LOG_LEV_CON)
    file_format = logging.Formatter(LOG_FILE_FORMAT, datefmt=LOG_DATE_FORMAT)
    console_format = logging.Formatter(LOG_CONSOLE_FORMAT)
    file_handler.setFormatter(file_format)
    console_handler.setFormatter(console_format)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return success


def example_virtual_environment():
    '''Standard example to illustrate virtual environment tools.

    Parameters
    ----------
    p_app_path
        Path to the application module
    p_cls
        Clear the screen before start
        Default is True

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_path | False ]

    Examples
    --------

    '''
    success = True
    venv_name = 'new-project'
    # Get the the venv activation command
    venv = activate_venv_cmd(get_tmp_fldr(), venv_name)
    print('Cmd example:\t{}'.format(venv))
    success = venv and success

    # Remove remains of any previous skeletons still hanging around.
    if get_os() == WINDOWS:
        p_cmd = ['rd', '/S', '/Q', get_venv_fldr(get_tmp_fldr(), venv_name)]
    elif get_os() in [LINUX, MACOS]:
        p_cmd = ['rm', '-f', '-r', get_venv_fldr(get_tmp_fldr(), venv_name)]
    success = exec_cmd(p_cmd, p_crash=False, p_verbose=True)

    # Instal a new venv including termcolor in a tmp directory
    package_list = [['Web', 'termcolor'], ['Web', 'wheel']]
    success = (
        set_up_venv(get_tmp_fldr(), venv_name, package_list, p_verbose=True) and success
    )

    # Install/upgrade in an existing venv
    instructions = [
        'ECHO Setting up the {} VEnv...'.format(venv_name),
        'pip install --upgrade wheel',
        'ECHO Done!',
    ]
    success = (
        install_in_venv(get_tmp_fldr(), venv_name, instructions, p_verbose=True)
        and success
    )
    result_rep(success, p_comment='Done')
    return success


def example_scripting():
    '''Standard example to illustrate standard use.

    Parameters
    ----------
    p_app_path
        Path to the application module
    p_cls
        Clear the screen before start
        Default is True

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_path | False ]

    Examples
    --------

    '''
    success = True
    # Run a few commands in a script.  Useful when executing commands in a
    # venv in the same session.
    tmp_test = get_tmp_fldr() / 'test'
    tmp_t1 = tmp_test / 'T1'
    if get_os() == WINDOWS:
        batch = [
            'md {}'.format(tmp_t1),
            'dir /B {}'.format(tmp_test),
        ]
    elif get_os() in [LINUX, MACOS]:
        batch = [
            'mkdir -p {}'.format(tmp_t1),
            'ls -l {}'.format(tmp_test),
        ]
    success = exec_batch_in_session(batch, p_verbose=False) and success

    # Execute some commands in a batch
    if get_os() == WINDOWS:
        cmds = [
            ['rd', '/S', '/Q', '{}'.format(tmp_t1)],
            ['md', '{}'.format(tmp_t1)],
            ['dir', '/B', '{}'.format(tmp_test)],
        ]
    elif get_os() in [LINUX, MACOS]:
        cmds = [
            ['mkdir', '-p', '{}'.format(tmp_t1)],
            ['ls', '-l', '{}'.format(tmp_test)],
        ]
    success = exec_batch(cmds) and success

    # Write a script
    script_pth = get_tmp_fldr() / _name
    cmds = [
        ['echo', 'Hello'],
        ['echo', 'Goodbye'],
    ]
    contents = write_script(script_pth, cmds)
    print(contents)

    # Create a few files to the previous example and the remove the tree
    t_file = tmp_test / Path('t.tmp')
    t_file.touch(mode=0o666, exist_ok=True)
    t_file = tmp_t1 / Path('t.tmp')
    t_file.touch(mode=0o666, exist_ok=True)
    success = rm_tree(tmp_test, p_crash=True) and success

    # Attempt to remove a temporary locked file.
    venv_name = 'new-project'
    success = rm_locked_file(get_venv_fldr(get_tmp_fldr(), venv_name)) and success

    # Read an option from an ini for a particular os and setup
    cnf = configparser.ConfigParser()
    cnf.read_dict(
        {
            'Folders': {
                'windows1_MyFolderOnSystem': 'c:\\Program Files',
                'windows2_MyFolderOnSystem': 'c:\\Program Files (x86)',
                'linux1_MyFolderOnSystem': '/usr/local/bin',
                'linux2_MyFolderOnSystem': '/bin',
                'macos1_MyFolderOnSystem': '/System',
                'macos2_MyFolderOnSystem': '/Application',
            }
        }
    )
    os_system_flder = select_os_fldr_from_config(cnf, 'Folders', 'MyFolderOnSystem')
    print(os_system_flder)
    success = os_system_flder and success
    result_rep(success, p_comment='Done')
    return success


def example_messaging():
    '''Standard example to illustrate standard use.

    Parameters
    ----------
    p_app_path
        Path to the application module
    p_cls
        Clear the screen before start
        Default is True

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
                MSG_LEN
            )
        )
    )
    print(msg_ok('This message is an OK message'))
    print(msg_info('This is an info message'))
    print(msg_milestone('This is a milestone message'))
    print(msg_error('This is a warning message'))
    result_rep(success, p_comment='Done')
    return success


def do_examples(p_app_path=None, p_cls=True):
    '''Example to illustrate usage

    Parameters
    ----------
    p_app_path
        Path to the application module
    p_cls
        Clear the screen before start
        Default is True

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_path | False ]

    Examples
    --------

    '''

    # Initate the Archiver
    success = True
    success = example_logging() and success
    b_tls = Archiver(__name__, _VERSION, __doc__.split('\n', maxsplit = 1)[0], p_app_path)
    b_tls.print_header(p_cls=p_cls)
    # success = example_virtual_environment() and success
    success = example_scripting() and success
    success = example_messaging() and success
    b_tls.print_footer()
    if success:
        return b_tls.archive_path
    return False


if __name__ == '__main__':
    do_examples(sys.argv[0])
# end __main__
