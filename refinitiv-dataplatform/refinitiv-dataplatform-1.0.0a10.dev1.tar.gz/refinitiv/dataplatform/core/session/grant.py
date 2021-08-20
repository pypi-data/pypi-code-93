# coding: utf-8


class Grant(object):
    def __init__(self, *args, **kwargs):
        if len(args):
            self._username = args[0]
        elif kwargs.get("username"):
            self._username = kwargs.get("username")
        else:
            self._username = None

    def get_username(self):
        return self._username

    def username(self, user_name):
        self._username = user_name
        return self
