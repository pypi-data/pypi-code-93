#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

from joker.textmanip import data


def test():
    print(
        data.get_all_encodings(),
        data.get_most_frequent_characters(),
        data.get_unicode_blocks(),
        sep='\n'
    )


if __name__ == '__main__':
    test()