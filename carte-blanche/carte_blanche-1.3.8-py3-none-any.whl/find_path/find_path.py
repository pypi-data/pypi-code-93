'''
=================================================================
Utility for generating root path from any module
-----------------------------------------------------------------
'''
import os
import sys
from os import path


KEYFILE = 'README.md'


def walk(keyfile=KEYFILE, start_file=__file__):
    '''walks backwards up path tree to find the project source directory using the given keyfile as a root'''
    hot_path = ''
    start_location = path.dirname(path.abspath(start_file))
    current_location = start_location

    root_toggle = False

    while root_toggle is False:
        files = os.listdir(current_location)

        if keyfile not in files:
            current_location = path.join(current_location, '..')

        else:
            hot_path = path.abspath(current_location)
            root_toggle = True

    sys.path.append(hot_path)

    return hot_path


if __name__ == '__main__':
    walk()
