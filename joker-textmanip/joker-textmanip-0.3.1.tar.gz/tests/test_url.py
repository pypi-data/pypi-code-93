#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

from joker.textmanip.url import URLMutable, url_simplify


def test_mutlink():
    s = 'https://www.youtube.com/results?search_query=buc'
    mlink = URLMutable(s)
    print(mlink)
    print(mlink.query)
    return mlink


def test_embed_link():
    h = 'https://github.com/'
    g = 'https://youtube.com/'
    k = 'embeded'
    urlmut = URLMutable(h)
    urlmut.embed_link(k, g)
    assert g == urlmut.unembed_link(k)


def test_url_simplify():
    import sys
    if sys.argv[1:]:
        s = sys.argv[1]
    else:
        s = 'https://www.example.com/a/bc?id=920&from=index#detail'
    print(url_simplify(s))


if __name__ == '__main__':
    lm = test_mutlink()
    test_mutlink()
    test_url_simplify()
