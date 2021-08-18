# This file is placed in the Public Domain.

"terminal"

import atexit
import os
import readline
import sys
import termios

resume = {}

def cprint(txt):
    print(txt)
    sys.stdout.flush()

    
def daemon():
    pid = os.fork()
    if pid != 0:
        termreset()
        os._exit(0)
    os.setsid()
    os.umask(0)
    si = open("/dev/null", "r")
    so = open("/dev/null", "a+")
    se = open("/dev/null", "a+")
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


def termsetup(fd):
    return termios.tcgetattr(fd)


def termreset():
    if "old" in resume:
        try:
            termios.tcsetattr(resume["fd"], termios.TCSADRAIN, resume["old"])
        except termios.error:
            pass


def termsave():
    try:
        resume["fd"] = sys.stdin.fileno()
        resume["old"] = termsetup(sys.stdin.fileno())
        atexit.register(termreset)
    except termios.error:
        pass

def wrap(func):
    termsave()
    try:
        func()
    except PermissionError:
        cprint("you need root privileges")
        return
    except KeyboardInterrupt:
        pass
    finally:
        termreset()
