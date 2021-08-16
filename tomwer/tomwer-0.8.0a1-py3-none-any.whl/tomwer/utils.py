# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["H. Payno", "T. Vincent"]
__license__ = "MIT"
__date__ = "04/01/2018"


import functools
from silx.utils.launcher import Launcher as _Launcher


def addHTMLLine(txt):
    return "<li>" + txt + "</li>"


def _docstring(dest, origin):
    """Implementation of docstring decorator.

    It patches dest.__doc__.
    """
    if not isinstance(dest, type) and isinstance(origin, type):
        # func is not a class, but origin is, get the method with the same name
        try:
            origin = getattr(origin, dest.__name__)
        except AttributeError:
            raise ValueError("origin class has no %s method" % dest.__name__)

    dest.__doc__ = origin.__doc__
    return dest


def docstring(origin):
    """Decorator to initialize the docstring from another source.

    This is useful to duplicate a docstring for inheritance and composition.

    If origin is a method or a function, it copies its docstring.
    If origin is a class, the docstring is copied from the method
    of that class which has the same name as the method/function
    being decorated.

    :param origin:
        The method, function or class from which to get the docstring
    :raises ValueError:
        If the origin class has not method n case the
    """
    return functools.partial(_docstring, origin=origin)


class Launcher(_Launcher):
    """
    Manage launch of module.

    Provides an API to describe available commands and feature to display help
    and execute the commands.
    """

    def print_help(self):
        """Print the help to stdout."""
        usage = self.usage
        if usage is None:
            usage = "usage: {0.prog} [--version|--help] <command> [<args>]"
        description = self.description
        epilog = self.epilog
        if epilog is None:
            epilog = "See '{0.prog} help <command>' to read about a specific subcommand"

        print(usage.format(self))
        print("")
        if description is not None:
            print(description)
            print("")
        print("The {0.prog} commands are:".format(self))
        commands = sorted(self._commands.keys())
        for command in commands:
            command = self._commands[command]
            print("   {:18s} {:s}".format(command.name, command.description))
        print("")
        print(epilog.format(self))
