"""This module contains the MainCLI class."""

from sys import argv, stdin, stdout, stderr, exit

# from . import Const
from unisos.gcipher import Const
from unisos.gcipher.cipher.KeyedCipher import InvalidKey
from unisos.gcipher.AutomaticClass import AutomaticClass

class MainCLI:

    """This class is responsible for command-line parsing, etc."""

    def __init__(self):
        """Run as a GNOME application or as a command-line application."""
        if len(argv) > 1:
            self._runCommandLineApplication()
        else:
            self._runGnomeApplication()
            
    def _runGnomeApplication(self):
        """Run as a GNOME application.
        
        This method does not return until the application is finished.
        
        """
        # import pygtk
        # pygtk.require("2.0")
        # import gtk
        # import gnome
        # from MainGUI import MainGUI
        # gnome.program_init(Const.NAME, Const.VERSION)
        # MainGUI()
        # gtk.main() 

    def _runCommandLineApplication(self):
        """Run as a command-line application.

        See the man page for a description of all of these arguments.  This
        method does not return until the application is finished.
        
        """
        from getopt import getopt, GetoptError
        operations = []
        proxyMode = False
        try:
            opts, args = getopt(argv[1:], "c:C:k:p")
            for o, v in opts:
                if o.lower() == "-c":
                    operations.append(_Operation(
                        cipher = v, 
                        encrypt = (o == "-c"),
                        key = None 
                    ))
                elif o == "-k":
                    if not len(operations):
                        usage("key specified before any ciphers", 1)
                    operations[-1].key = v
                elif o == "-p":
                    proxyMode = True
                else:
                    raise AssertionError("unhandled option %s" % o)
            if proxyMode:
                self._runProxyMode(operations, args)
            else:
                self._runFilterMode(operations, args)
        except GetoptError as e:
            usage(e.msg, 1)

    def _runProxyMode(self, operations, args):
        """Handle the rest of the arguments and run in proxy mode.

        This method does not return.

        """
        from .Proxy import Proxy
        import asyncore
        import socket
        if not len(args) == 3:
            usage("proxy mode requires exactly 3 arguments", 1)
        proxiedHost, proxiedPort, listeningPort = args
        try:
            Proxy(proxiedHost, 
                self._castToValidPort(proxiedPort), 
                self._castToValidPort(listeningPort),  
                self._composeOperations(operations),
                self._composeOperations(operations, True))
            asyncore.loop()
        except socket.error as e:
            stderr.write("%s: socket error: %s\n" % (Const.NAME, e.args[1]))
            exit(1)

    def _castToValidPort(self, port):
        """Cast and return port as a valid port or complain and exit."""
        MIN_PORT = 1
        MAX_PORT = 65536
        try:
            port = int(port)
            assert MIN_PORT <= port and port <= MAX_PORT
            return port
        except:
            stderr.write("%s: '%s' is not a valid port\n" % (Const.NAME, port))
            exit(1)

    def _runFilterMode(self, operations, args):
        """Handle the rest of the arguments and run in filter mode.

        This method does not return until the application is finished.

        """
        lenargs = len(args)
        input = stdin
        output = stdout
        try:
            if lenargs >= 1 and args[0] != "-":
                input = open(args[0], "r")
            if lenargs == 2 and args[1] != "-":
                output = open(args[1], "w")
            if lenargs > 2:
                usage("too many arguments", 1)
            operationsFunction = self._composeOperations(operations)
            while 1:
                line = input.readline()
                if not line:
                    break
                output.write(operationsFunction(line))
            if input != stdin:
                input.close()
            if output != stdin:
                output.close()
        except IOError as e:
            stderr.write("%s: %s: %s\n" % (Const.NAME, e.filename, e.strerror))
            exit(1)

    def _composeOperations(self, operations, invert=False):
        """Call getFunction for each operation and compose a closure.

        invert - Should the meaning of the encrypt attribute for each operation
        be reversed?

        """

        def closure(s):
            """Apply all of the operations on s, and return it."""
            for f in functions:
                s = f(s)
            return s

        functions = [i.getFunction(invert) for i in operations]
        return closure


class _Operation(AutomaticClass):

    """This is a simple class representing an encryption operation.
    
    The following attributes are used:

    cipher - This string is the name of a cipher.
    encrypt - If true, do encrypt.  Otherwise, do decrypt.
    key - This string is the key to use with the cipher.

    """

    def getAttributes(self):
        return AutomaticClass.getAttributes(self) + [
            "cipher", "encrypt", "key"]

    def getFunction(self, invert = False):
        """This is a factory for a function representing this _Operation.
        
        Instantiate the cipher, set the key, and return either the encrypt or
        decrypt function.  This function may call usage and exit.

        invert - Should the meaning of the encrypt attribute be reversed?

        """
        try: 
            CipherModule = __import__("unisos.gcipher.cipher." + self.cipher, globals(),
                locals(), self.cipher)
            CipherClass = getattr(CipherModule, self.cipher)
            cipherInstance = CipherClass()
            if hasattr(cipherInstance, "key"):
                if self.key != None:
                    cipherInstance.key = self.key
            else:
                if self.key != None:
                    usage("no key required for cipher '%s'" % self.cipher, 1)
            if self.encrypt or invert:
                return cipherInstance.encrypt
            else:
                return cipherInstance.decrypt
        except ImportError:
            usage("failed to import cipher '%s'" % self.cipher, 1)
        except InvalidKey as e:
            # usage("invalid key '%s' for cipher '%s'; it's not '%s'." %
            #     (e.key, operation.cipher, e.keyDescription), 1)
            usage("invalid key '%s' for cipher '%s'; it's not '%s'." %
                (e.key, self.cipher, e.keyDescription), 1)

            

def usage(warning=None, exitCode=None):
    """Print usage information.

    warning - If this is not None, it will be printed as well.

    exitCode - If this is not None, the application will exit with this 
    exit code.

    """
    if warning:
        stderr.write("%s: %s\n" % (Const.NAME, warning))
    stderr.write("Try `man %s' for more information.\n" % Const.NAME)
    if exitCode != None:
        exit(exitCode)
