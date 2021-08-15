import sys
from .bar_modules import TextModule, BarModule, ValueModule, PercentageModule, EtaModule


class ProgressBar:
    EXPECTED_GENERATION_STRING_ARGS = ['bar', 'val']

    def __init__(self, *args):
        self.state = 0
        self.string = ''
        self.modules = []

        if len(args) == 0:
            pass
        elif len(args) == 1 and type(args[0]) == str:
            generation_string = args[0]
            current_string = ''
            readindex = 0
            while readindex < len(generation_string):
                next_char = generation_string[readindex]
                if next_char == '\\':
                    self.add_text(current_string)
                    current_string = ''
                current_string += next_char
                if current_string != '':
                    if current_string[0] == '\\' and next_char == ')':
                        mod_type, argstring = current_string[1:-1].split('(')
                        args = argstring.split(',')
                        if mod_type == 'bar':
                            self.add_bar(int(args[0]))
                        elif mod_type == 'val':
                            if len(args) == 2:
                                self.add_value(args[0], int(args[1]))
                            else:
                                self.add_value(args[0])
                        elif mod_type == 'eta':
                            if args != ['']:
                                self.add_eta(int(args[0]))
                            else:
                                self.add_eta()
                        else:
                            raise NameError(
                                f"Specified module type doesn't exist. "
                                f"Got {mod_type}, check self.EXPECTED_GENERATION_STRING_ARGS for possible arguments"
                            )
                        current_string = ''
                    elif current_string == '\\%':
                        self.add_percentage()
                        current_string = ''
                readindex += 1
            self.add_text(current_string)

        else:
            raise TypeError('Wrong argument type or too much args')

    def __repr__(self):
        return self.string

    def _flush(self):
        for module in self.modules:
            sys.stdout.write('\r' * module.length)
            sys.stdout.flush()

    def _display(self):
        sys.stdout.write(self.string)
        sys.stdout.flush()

    def update(self, *args):
        self.string = ''
        for module in self.modules:
            module.update(*args)
            self.string += module.string
        self._flush()
        self._display()

    def finish(self):
        self.string = ''
        for module in self.modules:
            module.finish()
            self.string += module.string
        self._flush()
        self._display()
        print()

    def add_text(self, text):
        self.modules.append(TextModule(text))

    def add_bar(self, barlen):
        self.modules.append(BarModule(barlen))

    def add_value(self, identifier, barlen=5):
        self.modules.append(ValueModule(identifier, barlen))

    def add_percentage(self):
        self.modules.append(PercentageModule())

    def add_eta(self, alloc_space=8):
        self.modules.append(EtaModule(alloc_space))
