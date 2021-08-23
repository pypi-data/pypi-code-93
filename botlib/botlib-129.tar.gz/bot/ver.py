# This file is placed in the Public Domain.

__version__ = 129

def __dir__():
    return ("ver",)

txt = "botlib"

def ver(event):
    event.reply("BOT %s - %s" % (__version__, txt))
