#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import sys

from joker.textmanip.stream import AtomicTailer


def xp_atomic_tailer():
    path = sys.argv[1]

    atx = AtomicTailer(path, timeout=5)

    for i, line in enumerate(atx):
        print(i, repr(line))

    print('\n\n\n')

    atx = AtomicTailer(path, timeout=5)

    for lines in atx.follow_lines(3):
        for i, line in enumerate(lines):
            print(i, repr(line))


if __name__ == '__main__':
    xp_atomic_tailer()
