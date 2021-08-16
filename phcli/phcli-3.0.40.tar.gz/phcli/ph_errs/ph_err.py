# -*- coding: utf-8 -*-


class PhException(Exception):
    def __init__(self, *args, **kwargs):
        self.msg = args[0] if args else 'Pharbers Unknow Exception'

    def __str__(self):
        return repr(self.msg)


class PhRuntimeError(RuntimeError):
    """The Pharbers Exceptions

        Args:
            code: the number of exceptions
            msg: the message of exceptions

    """

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg


# Maxauto 1 - 99
exception_file_already_exist = PhRuntimeError(-1, "The File Is Already Exists")
exception_file_not_exist = PhRuntimeError(-2, "The File Is Not Exists")
exception_function_not_implement = PhRuntimeError(-3, "the function is not implement, please contact "
                                                      "alfredyang@pharbers.com")
exception_not_found_preset_job = PhRuntimeError(-4, "this preset job is non-existent")

# Lambda 100 - 199
