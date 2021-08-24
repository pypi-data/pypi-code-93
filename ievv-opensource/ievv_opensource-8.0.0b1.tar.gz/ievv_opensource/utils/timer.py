import sys
from datetime import datetime


class TimeExecution(object):
    """
    Times the execution of code that is run within, and outputs with label to the

    Example:

        from ievv_opensource.utils.timer import TimeExecution
        from time import sleep
        from random import randint

        with TimeExecution(label='foo', output_function=print):
            sleep(randint(1,3))

        with TimeExecution(label='bar', output_function=logger.critical):
            sleep(randint(1,3))
    """
    def __init__(self, label, output_function=sys.stdout.write):
        self.label = label
        self.output_function = output_function
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()

    def __exit__(self, ttype, value, traceback):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        self.output_function(f'{self.label}: {duration} seconds')
