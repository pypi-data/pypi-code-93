import datetime
import threading

import flask
import my_pickledb


class Logging:
    class FMTS:
        DEFAULT = "{0} [ {1} ]"
        MESSAGE_ONLY = "{0}"
        TIME_ONLY = "{1}"

    def __init__(self, location: str = "plsl.log"):
        """
        Creates a logging object containing Flask Class and PickleDB Class
        It modifies PickleDB save method to custom one

        It will start Flask Server automatically on daemon mode, so if program stops, it will stop after it

        :param location:
        """

        def save( ):
            with open(location, "w") as f: [f.write(f"{type_.upper()} : {value} \n") for type_, values in self.database().items() for value in values]

        self.database = my_pickledb.PickleDB(location=location, load=False, auto_dump=True)
        self.database.database = {
            "info": [],
            "debug": [],
            "warning": [],
            "error": []
        }
        self.database.save = save

    """
    All methods below works in the same way
    It will add a message to specified logging type:
        - info
        - debug
        - warning
        - error
        
    How to use datetime_format?
    Check datetime format codes here: https://www.w3schools.com/python/gloss_python_date_format_codes.asp
    
    How to use str_format?
    Parameters:
        0 -> message
        1 -> datetime
    Add as many args as you want, indexing is important, 0 and 1 are reserved to message and datetime
    You can also use kwargs as parameters, it uses .format()    
    """

    def info(self, message: str, *args, datetime_format: str = "%d-%b-%Y %H:%M:%S", str_format: str = FMTS.DEFAULT, **kwargs): self.database.append("info", str_format.format(message, datetime.datetime.now().strftime(datetime_format), *args, **kwargs))

    def debug(self, message: str, *args, datetime_format: str = "%d-%b-%Y %H:%M:%S", str_format: str = FMTS.DEFAULT, **kwargs): self.database.append("debug", str_format.format(message, datetime.datetime.now().strftime(datetime_format), *args, **kwargs))

    def warning(self, message: str, *args, datetime_format: str = "%d-%b-%Y %H:%M:%S", str_format: str = FMTS.DEFAULT, **kwargs): self.database.append("warning", str_format.format(message, datetime.datetime.now().strftime(datetime_format), *args, **kwargs))

    def error(self, message: str, *args, datetime_format: str = "%d-%b-%Y %H:%M:%S", str_format: str = FMTS.DEFAULT, **kwargs): self.database.append("error", str_format.format(message, datetime.datetime.now().strftime(datetime_format), *args, **kwargs))


class WebLogging(Logging):
    def __init__(self, location: str = "plsl.log", **kwargs):
        super().__init__(location)

        self.server = flask.Flask(__name__, **kwargs)

        @self.server.route("/")
        def logging( ): return flask.render_template("index.html", database=self.database.database.items())

        threading.Thread(target=self.server.run, args=("0.0.0.0", 9999,), daemon=True).start()
