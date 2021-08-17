#!/usr/bin/env python3
from urllib.request import Request, urlopen
from .parsers import StopParsing


HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.111 Safari/537.36 Edge/86.0.622.51"
        ),
        "Accept": "text/html, application/xhtml+xml, image/jxr, */*",
        "Accept-Language": "ru-RU"
    }


def request(url):
    return urlopen(Request(url, headers=HEADERS))


def parser_run(parser, data):
    try:
        parser.feed(data)
    except StopParsing:
        pass
    finally:
        parser.reset()
        parser.close()
    return parser

def titles_human(parser_seasons):
    titles = {}
    for i, j in parser_seasons.items():
        title = j[0]
        if len(j) > 1:
            title = "/".join(j)
        titles[i] = title
    return titles
