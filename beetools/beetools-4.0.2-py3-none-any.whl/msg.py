
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

from pathlib import Path
import sys
from termcolor import colored
import beetools as bt

_path = Path(__file__)
_name = _path.stem
_VERSION = '3.2.0'

# Message defaults
BAR_LEN = 50
MSG_LEN = 50
CRASH_RETRY = 2


def display(p_msg, p_len=MSG_LEN, p_color='white') -> str:
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
    >>> from beetools import msg.display
    >>> msg.display( 'Display message' )
    '\\x1b[37mDisplay message                               '

    '''
    msg = colored('{: <{len}}'.format(p_msg, len=p_len), p_color)
    return msg[:p_len] + ' '


def error(p_msg) -> str:
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


def header(p_msg) -> str:
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


def info(p_msg) -> str:
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


def milestone(p_msg) -> str:
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


def ok(p_msg) -> str:
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
        display(
            'This message print in blue and cut at {} character because it is too long!'.format(MSG_LEN), p_color = 'blue'
        )
    )
    print(ok('This message is an OK message'))
    print(info('This is an info message'))
    print(milestone('This is a milestone message'))
    print(error('This is a warning message'))
    bt.result_rep(success, p_comment='Done')
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
    success = True
    b_tls = bt.Archiver(_name, _VERSION, __doc__.split('\n')[0], p_app_path)
    b_tls.print_header(p_cls=p_cls)
    success = example_messaging() and success
    b_tls.print_footer()
    if success:
        return b_tls.archive_pth
    return False


if __name__ == '__main__':
    do_examples(sys.argv[0])
