#!/usr/bin/env python3
from time import sleep
from collections import namedtuple
from urllib.error import URLError
from urllib.parse import urlparse, urljoin, quote
from .parsers import ImdbSearchParser, KinopoiskSearchParser, \
    KinopoiskParser, ImdbParser, KinopoiskSeriesParser, ImdbSeriesParser
from .utils import request, parser_run, titles_human


def new(url):
    if urlparse(url).netloc not in ("www.imdb.com", "www.kinopoisk.ru"):
        raise ValueError("only www.imdb.com and www.kinopoisk.ru are allowed")
    if "kinopoisk" in url:
        parser_film = KinopoiskParser
        parser_series = KinopoiskSeriesParser
        if "https" in url:
            url = url.replace("https", "http")
    else:
        parser_film = ImdbParser
        parser_series = ImdbSeriesParser
    try:
        response = request(url)
    except URLError:
        return None
    p = parser_run(parser_film(),
        response.read().decode("utf8", errors="ignore"))
    Film = namedtuple("Film", "title alternate year time age")
    f = Film(p.title, p.alternate, p.year, p.time, p.age)
    if p.isfilm:
        return f
    Film = namedtuple("Film", Film._fields + ("titles",))
    sleep(1)
    try:
        response = request(urljoin(url, "episodes/"))
    except URLError:
        return f
    ps = parser_run(parser_series(),
        response.read().decode("utf8", errors="ignore"))
    titles = titles_human(ps.seasons)
    s = Film(p.title, p.alternate, p.year, p.time, p.age, titles)
    if "imdb" in url:
        u = urljoin(url, "episodes?season=")
        try:
            season_last = int(ps.season)
        except ValueError:
            return s
        for i in range(1, season_last):
            try:
                response = request(u+str(i))
            except URLError:
                continue
            ps = parser_run(parser_series(),
                response.read().decode("utf8", errors="ignore"))
            titles.update(titles_human(ps.seasons))
            sleep(0.5)
        s = Film(p.title, p.alternate, p.year, p.time, p.age, titles)
    return s


def search(word):
    if len(word) < 2:
        return []
    result = []
    word = quote(word)
    for url, parser in (
      ("https://www.imdb.com/find?q=", ImdbSearchParser),
      ("https://www.kinopoisk.ru/index.php?kp_query=", KinopoiskSearchParser)):
        try:
            response = request(url + word)
        except URLError:
            continue
        data = response.read().decode("utf8", errors="ignore")
        if "kinopoisk" in url and \
           ("film" in response.url or "series" in response.url):
                p = parser_run(KinopoiskParser(), data)
                name = "{} / {} ({})".format(p.title, p.alternate, p.year)
                found = [(name, response.url)]
        else:
            found = parser_run(parser(), data).list
            found = [(i, urljoin(url, j)) for i, j in found]
        result += found
    return result
