# Standard library imports.
import argparse
import io
import os
import sys
from _io import TextIOWrapper


class TextType(object):

    def __init__(self, bufsize = -1, encoding = None, errors = None):

        self._mode = 'r'
        self._bufsize = bufsize
        self._encoding = encoding
        self._errors = errors

        return None

    def __call__(self, string):

        # The return value/object.
        value = None

        if string == '':
            raise valueError('empty argument for TextType')

        elif string == '-':
            value = sys.stdin

        elif os.path.isfile(str(string)) == True:

            try:
                value = open(
                    string,
                    self._mode,
                    self._bufsize,
                    self._encoding,
                    self._errors)

            except OSError as e:

                message = 'unable to open \'%s\': \'%s\''
                raise ArgumentTypeError(message % (string, e))

        elif type(string) == type(''):
            value = io.StringIO(string)

        else:
            raise valueError('invalid argument for TextType')

        return value

    def __repr__(self):

        args = self._mode, self._bufsize
        kwas = [('encoding', self._encoding), ('errors', self._errors)]
        astr = ', '.join(
            [repr(arg) for arg in args if arg != -1]
                + ['%s=%r' % (kw, arg) for kw, arg in kwas if arg is not None])

        return '%s(%s)' % (type(self).__name__, astr)


class Command(object):

    def create_argparser(self):

        # Create the argument parser.
        parser = argparse.ArgumentParser()

        # Add an optional argument prior to calling the "add_arguments"
        # method.  Any class that uses this class as a base will
        # automatically have the "add2path" functionality added.
        parser.add_argument(
            '--add2path',
            nargs = '*',
            help = 'Add to the Python path')

        # Add more arguments.  This method should be extended by any
        # classes using this class as a base.
        self.add_arguments(parser)

        return parser

    def add_arguments(self, parser):

        parser.add_argument(
            '--infile',
            type = TextType(),
            default = sys.stdin,
            help = 'File containing input data for this command')

        return None

    def clean(self, **kwargs):

        cleaned = {}

        return cleaned

    def dumps(self, value, **kwargs):
        """Dump the "handle" method's return value to a string.

        """
        return str(value)

    def handle(self, *args, **kwargs):

        # This is just an example of how the Command should work.
        # Child classes should override this completely.
        data_in = kwargs.get('infile').read()

        # Return the "sys.path", if the "data_in" is empty.
        if data_in == '':
            data_in = str(sys.path)

        return data_in

    def stdout(self, text):

        if not text.endswith('\r\n') or not text.endswith('\n'):
            text += '\n'

        try:

            sys.stdout.write(text)
            sys.stdout.flush()

        except BrokenPipeError as e:

            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())

            # Exit the script with an error code.
            sys.exit(1)

        return None

    def stderr(self, text):

        if not text.endswith('\r\n') or not text.endswith('\n'):
            text += '\n'

        try:

            sys.stderr.write(text)
            sys.stderr.flush()

        except BrokenPipeError as e:

            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stderr.fileno())

            # Exit the script with an error code.
            sys.exit(1)

        return None

    @staticmethod
    def add2path(new_path):

        # The "new_path" parameter may be a relative path, so get the
        # absolute path for the given parameter.
        new_path = os.path.abspath(new_path)

        # Make sure the "new_path" parameter is lowercase when running
        # on the Windows flavor of an Operating Systemp.
        if sys.platform == 'win32':
            new_path = new_path.lower()

        # Determine if the "new_path" exists.  If so, attempt to add to
        # the "sys.path".
        if os.path.exists(new_path) == True:

            # Define a flag that will indicate if the "new_path"
            # parameter should be added to the path.
            add = True

            for x in sys.path:

                # If a path in the "sys.path" is relative, get the
                # absolute path instead.  Used to check against the
                # "new_path" parameter.
                x = os.path.abspath(x)

                # Once again, make sure the path values are lowercase
                # when using on Windows.
                if sys.platform == 'win32':
                    x = x.lower()

                if new_path in (x, x + os.sep):
                    add = False

            # If a match was not found, add the "new_path" value
            # to the path.  Set the counter
            if add == True:
                sys.path.append(new_path)

        return None

    @classmethod
    def get_handled(cls, *args, **kwargs):
        """Returns the Command instance after the handle method is run.

        """
        cmd = cls()
        cmd.handle(*args, **kwargs)

        return cmd

    @classmethod
    def run(cls, *args):
        """Runs the command as a command line script.

        """
        # Define the return value.  If invoked via the command line,
        # then this variable should be returned as a NoneType.
        output = None

        # Creates a Two-Percent Command class instance.
        cmd = cls()

        # Parse the command line arguments into a Namespace instance.
        # Input may also include a stdin pipe, if defined in the
        # "add_arguments" method.  If the args parameter is a list of
        # string arguments, then attempt to parse the string arguments
        # instead of the command line arguments.
        parser = cmd.create_argparser()
        kwargs = {}

        if len(args) == 1:
            if type(args[0]) == type([]):
                kwargs = vars(parser.parse_args(args[0]))

        else:
            kwargs = vars(parser.parse_args())

        # Create the kwargs variable.  Loop over the arguments to find
        # a TextIOWrapper class.  If found, then check if its name is
        # "<stdin>".  If so, check if stdin is empty.  If so, then set
        # the keyword argument to an empty StringIO class.  This fixes
        # the possibility for the program to hang.
        #kwargs = vars(ns)

        for k in kwargs.keys():
            if type(kwargs[k]) == TextIOWrapper:
                if kwargs[k].name == '<stdin>':
                    if sys.stdin.isatty():
                        kwargs[k] = io.StringIO()

        # Process any new additions to the "sys.path" via the
        # "add2path" argparse argument.
        if type(kwargs.get('add2path')) == type([]):
            for new_path in kwargs['add2path']:
                if type(new_path) == type(''):
                    cls.add2path(new_path)

        # Remove the "add2path" key/value pair from the keyword
        # arguments.  Not needed in the "handle" method.
        if kwargs.get('add2path', None) is not None:
            del kwargs['add2path']

        # Prior to calling the "handle" method, call the clean method to
        # perform any final checks or conversions.  Then, call the
        # handle method, processing the input data and returning any
        # output.
        #h_out = None

        try:

            # Prepare the command line keyword arguments for use by the
            # handle method.
            cleaned = cmd.clean(**kwargs)

            if type(cleaned) == type({}):
                if len(cleaned.keys()) > 0:
                    kwargs.update(cleaned)

            output = cmd.handle(**kwargs)

        except Exception as e:

            output = None
            cmd.stderr('Error: {}'.format(str(e)))

        # If output is not None, then attempt to convert the output
        # object to a string so that the value may be printed on the
        # command line.  However, if this "run" classmethod was passed
        # a list of arguments, then do not print the output object.
        # Instead, return the object as is.
        if type(output) != type(None):

            if len(args) == 0:

                try:

                    _o = cmd.dumps(output, **kwargs)

                    if type(_o) == type(''):
                        if _o != '':
                            cmd.stdout(_o)

                except Exception as e:
                    cmd.stderr(
                        'An error occurred attempting to print output: {}'\
                            .format(str(e)))

                output = None

        return output


def main(*args):
    Command.run(*args)


if __name__ == '__main__':

    # Call the Command.
    main()

