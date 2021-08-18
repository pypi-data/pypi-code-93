#!/usr/bin/env python3
# This file is placed in the Public Domain.

import base64
import os
import sys

def pwd(event):
    if len(event.args) != 1:
        event.reply("pwd <nick> <password>")
        return
    m = "\x00%s\x00%s" % (event.cmd, event.args[0])
    mb = m.encode('ascii')
    bb = base64.b64encode(mb)
    bm = bb.decode('ascii')
    event.reply(bm)
