class main_logger:

    from datetime import datetime
    start_at = None
    flow = ""
    __main_filename__ = ""
    __levels__ = {
        "info" : 0,
        "warnings" : 1,
        "errors" : 2
    }

    def __init__(self, module, level = "info"):

        from pathlib import Path
        from _pickle import dump

        level = self.__levels__[level]
        # Set level of logs
        self.__info_lv__ = level >= 0
        self.__warning_lv__ = level >= 1

        # Create format and file management
        self.__sub_module__ = False
        self.start_at = self.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.flow = module.__name__
        self.__format__ = "{0} - " + f"flow: {module.__name__} - " + " - {1}: {2}\n"
        Path(f"logs/{self.flow}_{self.start_at}").mkdir(parents=True, exist_ok=True)
        self.__main_filename__ = f"logs/{self.flow}_{self.start_at}/{module.__type__}_{module.__name__}.log"

        message = self.__format__.format(self.datetime.now().strftime("%Y-%m-%d_%H%M%S"), "INFO", f"{module.__type__} {module.__name__} start at {self.datetime.now().strftime('%Y-%m-%d_%H%M%S')}")
        self.write(message)

        with open("temp/log_conf", "wb") as file:
            dump({"flow": self.flow, "start_at" : self.start_at, "main_filename": self.__main_filename__}, file)

    def write(self, message):
        self.__main_file__ = open(self.__main_filename__, "a")
        self.__main_file__.write(message)

    def error(self, message):
        self.__main_file__ = open(self.__main_filename__, "a")
        self.__main_file__.write(self.__format__.format(self.datetime.now().strftime("%Y-%m-%d_%H%M%S"), "ERROR", message))


class logger:

    from datetime import datetime
    from _pickle import load
    __levels__ = {
        "info" : 0,
        "warnings" : 1,
        "errors" : 2
    }

    def __init__(self, module, level = "info"):

        from pathlib import Path

        # Set level of logs
        level = self.__levels__[level]
        self.__info_lv__ = level == 0
        self.__warning_lv__ = level <= 1

        # Create format and file management
        with open("temp/log_conf", "rb") as file:
            log_confs = self.load(file)
            self.flow = log_confs["flow"]
            self.start_at = log_confs["start_at"]
            self.__main_filename__ = log_confs["main_filename"]

        self.__format__ = "{0} - " + f"{module.__type__}: {module.__name__}" + " - {1}: {2}\n"
        self.__filename__ = f"logs/{self.flow}_{self.start_at}/{module.__type__}_{module.__name__}.log"

        self.info(f"{module.__type__} {module.__name__} start at {self.datetime.now().strftime('%Y-%m-%d_%H%M%S')}")

    def __write__(self, message):
        self.__write_in__(self.__filename__, message)
        self.__write_in__(self.__main_filename__, message)

    def __write_in__(self, filename, message):
        file = open(filename, "a")
        file.write(message)

    def __generate_message__(self, level, message):
        return self.__format__.format(self.datetime.now().strftime("%Y-%m-%d_%H%M%S"), level, message)

    def info(self, message):
        if self.__info_lv__:
            message = self.__generate_message__("INFO", message)
            self.__write__(message)

    def warning(self, message):
        if self.__warning_lv__:
            message = self.__generate_message__("WARNING", message)
            self.__write__(message)

    def error(self, message):
        message = self.__generate_message__("ERROR", message)
        self.__write__(message)
