from __future__ import absolute_import
from __future__ import unicode_literals

class ColorPrint(object):
    colors = {
        "red": 31,
        "green": 32
    }

    @classmethod
    def get(cls, msg, color="red"):
        return "\033[1;{}m{}\033[0m".format(cls.colors[color.lower()], msg)

    @classmethod
    def print(cls, msg, color="red"):
        print("\033[1;{}m{}\033[0m".format(cls.colors[color.lower()], msg))