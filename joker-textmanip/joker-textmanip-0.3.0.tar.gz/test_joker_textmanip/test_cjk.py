#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

from joker.textmanip.cjk import (
    remove_cjk, remove_spaces_beside_cjk, remove_spaces_between_cjk, integer_to_chsi
)


def test_integer_to_chsi():
    assert integer_to_chsi(127000) == '一十二万七千'
    assert integer_to_chsi(127001) == '一十二万七千零一'
    assert integer_to_chsi(2127000127000) == '二万一千二百七十亿一十二万七千'


def rp(o):
    print(repr(o))


def test_cjk_remove():
    s = " democracy 德 先生 science 赛 先生 "
    t = " democracy   science   "
    r = remove_cjk(s)
    assert t == r, rp(r)

    s = " democracy 德 先生 science 赛 先生 "
    t = " democracy德先生science赛先生"
    r = remove_spaces_beside_cjk(s)
    assert t == r, rp(r)

    s = " democracy 德 先生 science 赛 先生 "
    t = " democracy 德先生 science 赛先生 "
    r = remove_spaces_between_cjk(s)
    assert t == r, rp(r)


if __name__ == '__main__':
    test_cjk_remove()
