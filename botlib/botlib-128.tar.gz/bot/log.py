# This file is in the Public Domain.

from ob import Object


class Log(Object):
    def __init__(self):
        super().__init__()
        self.txt = ""


def log(event):
    if not event.rest:
        event.reply("log <txt>")
        return
    o = Log()
    o.txt = event.rest
    o.save()
    event.reply("ok")
