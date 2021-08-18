# This is file is placed in Public Domain.

import ob

def cmd(event):
    k = ob.krn.kernel()
    event.reply(",".join(sorted(k.cmds)))
