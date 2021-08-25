from . import paths
import os
import subprocess

def get_current_home_dir():
    return os.path.expanduser('~')


def execute_capture(command):
    os_exec = os.popen(command).read()
    return os_exec


def get_ip():
    return os.popen('ipconfig getifaddr en0').read()[:-1]


def waste():
    pass

def command(args: list, quite=False):
    if quite:
        sub = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    else:
        sub = subprocess.Popen(args)

    sub.wait()
    sub.kill()
    sub.terminate()

def remove(file):
    command(args=['rm', '-rf', file])


