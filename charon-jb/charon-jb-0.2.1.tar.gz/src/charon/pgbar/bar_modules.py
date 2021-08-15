import sys
import time


class ProgressBarModule:

    def __init__(self):
        self.length = 0
        self.string = ''

    def update(self, *args):
        pass

    def __repr__(self):
        return '<ProgressBarModule : ' + self.string + '>'

    def _display(self):
        sys.stdout.write(self.string)
        sys.stdout.flush()

    def finish(self):
        pass


class TextModule(ProgressBarModule):

    def __init__(self, text_string):
        super().__init__()
        self.string = text_string
        self.length = len(text_string)


class BarModule(ProgressBarModule):

    def __init__(self, barlength):
        super().__init__()
        self.length = 2 + barlength
        self.barlength = barlength
        self.string = '[' + ' ' * barlength + ']'

    def update(self, *args):
        arg = None
        if len(args) == 0:
            pass
        elif len(args) == 1:
            arg = args[0]
        elif len(args) == 2:
            if type(args[0]) == float or type(args[0]) == int:
                arg = args[0]
            elif type(args[1]) == float or type(args[1]) == int:
                arg = args[1]
        else:
            raise TypeError(f'Got too much arguments for update. Expected 0 to 2, got {len(args)}')
        if type(arg) == float or type(arg) == int:
            if arg > 1 or arg < 0:
                raise ValueError(f'The new state is wrong. Should be between 0 and 1. Got {arg}')
            self.string = '[' + int(arg * self.barlength) * '#' + (
                    self.barlength - int(arg * self.barlength)) * ' ' + ']'

    def finish(self):
        self.string = '[' + '#' * self.barlength + ']'


class ValueModule(ProgressBarModule):

    def __init__(self, identifier, length=5):
        super().__init__()
        self.identifier = identifier
        self.string = ' ' * length
        self.length = length

    def update(self, *args):
        arg = None
        if len(args) == 0:
            pass
        elif len(args) == 1:
            arg = args[0]
        elif len(args) == 2:
            if type(args[0]) == dict:
                arg = args[0]
            elif type(args[1]) == dict:
                arg = args[1]
        else:
            raise TypeError(f'Got too much arguments for update. Expected 0 to 2, got {len(args)}')
        if type(arg) == dict:
            if self.identifier in arg.keys():
                self.string = str(arg[self.identifier]) + ' ' * self.length
                self.string = self.string[:self.length]


class PercentageModule(ProgressBarModule):

    def __init__(self):
        super(PercentageModule, self).__init__()
        self.length = 5
        self.string = '  0 %'
        pass

    def update(self, *args):
        arg = None
        if len(args) == 0:
            pass
        elif len(args) == 1:
            arg = args[0]
        elif len(args) == 2:
            if type(args[0]) == float or type(args[0]) == int:
                arg = args[0]
            elif type(args[1]) == float or type(args[1]) == int:
                arg = args[1]
        else:
            raise TypeError(f'Got too much arguments for update. Expected 0 to 2, got {len(args)}')
        if type(arg) == float or type(arg) == int:
            if arg > 1 or arg < 0:
                raise ValueError(f'The new state is wrong. Should be between 0 and 1. Got {arg}')
            self.string = '  ' + str(int(100 * arg)) + ' %'
            self.string = self.string[-5:]

    def finish(self):
        self.string = '100 %'


class EtaModule(ProgressBarModule):

    def __init__(self, allocated_space=8):
        super().__init__()
        if allocated_space < 3:
            raise ValueError(f'Allocated space has to be greater than 2. Got {allocated_space}')
        self.length = allocated_space
        self.string = ' ' * (allocated_space - 2) + ' s'
        self.init_time = time.time()

    def update(self, *args):
        arg = None
        if len(args) == 0:
            pass
        elif len(args) == 1:
            arg = args[0]
        elif len(args) == 2:
            if type(args[0]) == float or type(args[0]) == int:
                arg = args[0]
            elif type(args[1]) == float or type(args[1]) == int:
                arg = args[1]
        else:
            raise TypeError(f'Got too much arguments for update. Expected 0 to 2, got {len(args)}')
        if type(arg) == float or type(arg) == int:
            if arg > 1 or arg < 0:
                raise ValueError(f'The new state is wrong. Should be between 0 and 1. Got {arg}')
            if arg == 0:
                pass
            else:
                time_taken = time.time() - self.init_time
                time_to_go = str((1 - arg) * time_taken / arg) + ' ' * self.length
                self.string = time_to_go[:self.length - 2] + ' s'

    def finish(self):
        if self.length >= 8:
            self.string = ' ' * (self.length - 8) + 'finished'
        else:
            self.string = '-' * self.length
