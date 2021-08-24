import colorama

colorama.init()


class LoggerLevels:
    info = 0
    warning = 1
    error = 2
    level_color = {info: '',
                   warning: colorama.Fore.YELLOW,
                   error: colorama.Fore.RED,
                   'end': colorama.Style.RESET_ALL}

    @classmethod
    def level_to_str(cls, level):
        if level == cls.info:
            return 'I'
        elif level == cls.warning:
            return 'W'
        elif level == cls.error:
            return 'E'
        else:
            return ''
