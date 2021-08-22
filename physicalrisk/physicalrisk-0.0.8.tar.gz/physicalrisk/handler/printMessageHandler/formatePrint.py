from timeit import default_timer as timer
import inspect
import re

class Formatter:
    # \033[  Escape code, this is always the same
    # 1 = Style, 1 for normal.
    # 32 = Text colour, 32 for bright green.
    # 40m = Background colour, 40 is for black.

    # class initialisation and stage flagging text
    @staticmethod
    def green(text):
        green='\033[0;32m'
        color_Off = '\033[0m'
        print(f'{green}{text}{color_Off}')

    @staticmethod
    def yellow(text):
        yellow ='\033[0;33m'
        color_Off = '\033[0m'
        print(f'{yellow}{text}{color_Off}')

    # Loading AWSdata format
    @staticmethod
    def cyan_background_with_white_text(text):
        cyan_white = '\033[0;30;46m'
        color_Off = '\033[0m'
        print(f'{cyan_white}{text}{color_Off}')

    # lambda expression
    @staticmethod
    def time_function_with_return(function):
        start = timer()
        result = function()
        end = timer()
        funcString = str(inspect.getsource(function))
        index = re.search('lambda: ', funcString).end() - 1
        funcString = funcString[index:len(funcString)-2]
        red ='\033[0;31m'
        color_off = '\033[0m'
        print(f'{red}The time spent on {funcString} is {end-start}{color_off}')
        return result

    # lambda expression
    @staticmethod
    def time_function_without_return(function):
        start = timer()
        function()
        end = timer()
        funcString = str(inspect.getsource(function))
        index = re.search('lambda: ', funcString).end() - 1
        funcString = funcString[index:len(funcString) - 2]
        red = '\033[0;31m'
        color_off = '\033[0m'
        print(f'{red}The time spent on{funcString} is {end-start}(s){color_off}')

