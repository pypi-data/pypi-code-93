#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

def try_me():
    total, used, free = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
    return f'Your RAM| total: {total}, used: {used}, free: {free}'

if __name__ == "__main__":
    message = try_me()
    print(message)
