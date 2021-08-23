#!/usr/bin/env python3
# This file is placed in the Public Domain.

import base64
import os
import sys

def __dir__():
    return ("pwd",)

def pwd(event):
    if len(event.args) != 2:
        event.reply("pwd <nick> <password>")
        return
    m = "\x00%s\x00%s" % (event.args[0], event.args[1])
    mb = m.encode('ascii')
    bb = base64.b64encode(mb)
    bm = bb.decode('ascii')
    event.reply(bm)
