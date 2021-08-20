import logging
import os
import sys
from datetime import datetime

from termcolor import colored


def get_timestamp():
    """
    Return the current timestamp formatted properly.
    @return: timestamp in string format
    """

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_message(message, status):
    """
    Generate the message in a format equal for all logs.
    """

    # Compute the timestamp to print before the log message
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"{t:<25} {status.upper():<25} {message}"


def generate_log_file_message(message, status):
    """
    Generate the message in a format equal for all logs.
    """

    # Compute the timestamp to print before the log message
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"{t};{status.upper()};{message};\n"


def write_to_log_file(filename, log):
    """
    Write the log in the file with append mode.

    @param filename: name of the file
    @param log: log to write
    """

    try:
        with open(os.path.join(os.getcwd(), filename), "a") as logfile:
            logfile.write(log)
    except:
        # TODO: da sistemare
        pass

    return True


class XanderLogger:
    """
    Custom logger for the tool. It overwrites the common log functions to create a custom log.
    The format is hardcoded but it is designed to provide a comfortable and readable output.
    """

    def __init__(self, console_log_level='info', log_folder='logs'):

        # Set the log level
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_log_level.upper())

        self.database = None

    def out(self, formatted_message, message, status):
        """
        The formatted message is printed on the stdout, the normal one instead is written in the DB and in the log file.
        @param message: simple string
        @param formatted_message: formatted and colored string
        @return: True
        """

        # Print on STDOUT
        print(formatted_message)

        try:
            if self.database:
                self.database.push(
                    query=f"INSERT INTO MESSAGES (DATA, STATO, MESSAGGIO) VALUES ({get_timestamp(), status, message})")
        except Exception:
            pass

        return True

    def success(self, message):
        """
        Print a message as info.
        """

        # Log color and status
        color = 'green'
        status = 'success'
        attrs = ['reverse', 'bold']

        # Message formatted in a log
        log = generate_message(message, status)

        self.out(message=message, status=status, formatted_message=colored(log, color, attrs=attrs))

    def info(self, message):
        """
        Print a message as warning.
        """

        # Log color and status
        color = 'white'
        status = 'info'

        # Message formatted in a log
        log = generate_message(message, status)

        self.out(message=message, status=status, formatted_message=log)

    def debug(self, message):
        """
        Print a message as warning.
        """

        # Log color and status
        color = 'grey'
        status = 'debug'

        # Message formatted in a log
        log = generate_message(message, status)

        self.out(message=message, status=status, formatted_message=colored(log, color))

    def network(self, message):
        """
        Print a message as warning.
        """

        # Log color and status
        color = 'magenta'
        status = 'network'

        # Message formatted in a log
        log = generate_message(message, status)

        self.out(message=message, status=status, formatted_message=colored(log, color))

    def error(self, message):
        """
        Print a message as error.
        """

        # Log color and status
        color = 'red'
        status = 'error'

        # Message formatted in a log
        log = generate_message(message, status)

        self.out(message=message, status=status, formatted_message=colored(log, color))

    def critical(self, *args):
        """
        Print a message as critical.
        """

        # Log color and status
        color = 'red'
        status = 'critical'
        attrs = ['reverse']

        for arg in args:
            # Message formatted in a log
            log = generate_message(arg, status)

            # Print the log
            print(colored(log, color, attrs=attrs))

            self.out(message=arg, status=status, formatted_message=colored(log, color, attrs=attrs))

        # End the engine because the critical error is a big problem for the execution flow
        exit(46)
