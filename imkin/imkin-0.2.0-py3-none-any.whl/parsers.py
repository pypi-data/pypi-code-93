#!/usr/bin/env python3
import json
from html.parser import HTMLParser


class StopParsing(Exception): pass


class BaseParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.alternate = ""
        self.year = ""
        self.time = ""
        self.age = ""
        self.isfilm = True


class ImdbParser(BaseParser):
    def __init__(self):
        super().__init__()
        self._script = False
        self._span = False
        self._spanRuntime = False
    
    def handle_starttag(self, tag, attrs):
        if tag == "script":
            for n, v in attrs:
                if n == "type" and v == "application/ld+json":
                    self._script = True
        elif tag == "span":
            for n, v in attrs:
                if n == "class" and "label" in v:
                    self._span = True
    
    def handle_data(self, data):
        if self._script:
            j = json.loads(data.strip())
            self.title = j["name"]
            alternate = j.get("alternateName", "")
            if alternate:
                self.alternate = alternate
            year = j["datePublished"]
            self.year = year.split("-")[0]
            time = j.get("duration", "")
            if time:
                if time.startswith("PT"):
                    time = time.lower().split("h")
                    hours = "".join(i for i in time[0] if i.isdigit())
                    minutes = "".join(i for i in time[1] if i.isdigit())
                    try:
                        self.time = str(int(hours) * 60 + int(minutes))
                    except ValueError:
                        pass
            self.age = j["contentRating"]
            self.isfilm = True if j["@type"] == "Movie" else False
        elif self._span and data == "Runtime":
                self._spanRuntime = True
        elif self._spanRuntime and self._span:
            data = data.strip()
            if data.endswith("min"):
                self.time = "".join(i for i in data if i.isdigit())
                raise StopParsing()

    def handle_endtag(self, tag):
        if tag == "script" and self._script:
            self._script = False
            if self.time:
                raise StopParsing()


class KinopoiskParser(BaseParser):
    def __init__(self):
        super().__init__()
        self._script = False
        self._a = False
        self._span = False
    
    def handle_starttag(self, tag, attrs):
        if tag == "script":
            for n, v in attrs:
                if n == "type" and v == "application/ld+json":
                    self._script = True
        elif tag == "a":
            for n, v in attrs:
                if not self.age and n == "class" and "restrictionLink" in v:
                    self._a = True
        elif tag == "span" and self._a:
            self._span = True
    
    def handle_data(self, data):
        if self._script:
            j = json.loads(data.strip())
            self.title = j["name"]
            alternate = j.get("alternateName", "")
            if alternate:
                self.alternate = alternate
            self.year = j["datePublished"]
            self.time = j["timeRequired"]
            self.isfilm = True if j["@type"] == "Movie" else False
            self._script = False
        elif self._span:
            if "+" in data:
                self.age = data.strip()

    def handle_endtag(self, tag):
        if self._span:
            raise StopParsing()


class BaseSeriesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.seasons = {}
        self.season_titles = []
        self.season = ""
        self.episode = ""


class ImdbSeriesParser(BaseSeriesParser):
    def __init__(self):
        super().__init__()
        self._option = False
        self._meta_episodes = 0
        self._div_eplist = False
        self._div_list_item = False
        self._meta = False
        self._strong = False
    
    def handle_starttag(self, tag, attrs):
        if tag == "option" and not self._option:
            for n, v in attrs:
                if n == "selected" and v == "selected":
                    self._option = True
                    continue
                if n == "value" and self._option:
                    self.season = v
                    return
        if tag == "div":
            for n, v in attrs:
                if n == "class" and "eplist" in v:
                    self._div_eplist = True
                    return
                if n == "class" and "list_item" in v and self._div_eplist:
                    self._div_list_item = True
                    return
        if tag == "meta":
            ep_num = False
            q = False
            for n, v in attrs:
                if n == "itemprop" and v == "episodeNumber" and \
                   self._div_list_item:
                    ep_num = True
                if n == "itemprop" and v == "numberofEpisodes" and \
                   self._meta_episodes == 0:
                    q = True
            for n, v in attrs:
                if n == "content" and q:
                    try:
                        self._meta_episodes = int(v)
                    except ValueError as err:
                        print(err)
                    q = False
                    return
                if n == "content" and ep_num:
                    self.episode = v
                    self.seasons[self.season+"."+self.episode] = []
                    self._meta = True
                    ep_num = False
                    return
        if tag == "strong" and self._meta:
            self._strong = True
            return
    
    def handle_data(self, data):
        if self._strong:
            name = data.strip()
            if name:
                self.seasons[self.season+"."+self.episode].append(
                    name)
    
    def handle_endtag(self, tag):
        if self._strong:
            self._strong = False
            self._meta = False
            self._div_list_item = False
            if len(self.seasons) == self._meta_episodes:
                raise StopParsing()


class KinopoiskSeriesParser(BaseSeriesParser):
    def __init__(self):
        super().__init__()
        self._div_season_item = False
        self._a = False
        self._a_s = False
        self._table = False
        self._td = False
        self._span = False
        self._b = False
        self._span_original = False
    
    def handle_starttag(self, tag, attrs):
        if tag == "div" and not self._div_season_item:
            for n, v in attrs:
                if n == "class" and v == "season_item":
                    self._div_season_item = True
                    return
        if tag == "a" and self._div_season_item:
            for n, v in attrs:
                if n == "href" and v.startswith("#"):
                    self._a = True
                    season = v[2:]
                    self.season_titles.append(season)
                    self._a = False
                    return
        if tag == "a":
            for n, v in attrs:
                if n == "name" and v[1:] in self.season_titles:
                    s = v[1:]
                    self.season_titles.remove(s)
                    self.season = s
                    self._a_s = True
                    return
        if tag == "table" and self._a_s:
            self._table = True
            return
        if tag == "td" and self._table:
            self._td = True
            return
        if tag == "span" and self._td:
            if not self._span:
                self._span = True
                return
            else:
                for n, v in attrs:
                    if n == "class" and v == "episodesOriginalName":
                        self._span_original = True
                        return
        if tag == "b" and self._span:
            self._b = True
            return
    
    def handle_data(self, data):
        if self._div_season_item:
            self._div_season_item = False
        elif self._b or self._span_original:
            name = data.strip()
            if name:
                self.seasons[self.season+"."+self.episode].append(
                    name)
        elif self._span and not self._b:
            episode = data.strip()
            if "Эпизод" in episode:
                ep = episode.split()[-1]
                self.seasons[self.season+"."+ep] = []
                self.episode = ep
    
    def handle_endtag(self, tag):
        if tag == "b" and self._b:
            self._b = False
        if tag == "span" and self._span_original:
            self._td = False
            self._span = False
            self._span_original = False
        if tag == "table" and self._table:
            self._table = False
            self._a_s = False
            if not self.season_titles:
                raise StopParsing()


class BaseSearch(HTMLParser):
    def __init__(self):
        super().__init__()
        self.list = []
        self._name = ""
        self._url = ""


class ImdbSearchParser(BaseSearch):
    def __init__(self):
        super().__init__()
        self._table = False
        self._td = False
        self._a = False
    
    def handle_starttag(self, tag, attrs):
        if tag == "table" and not self._table:
            for n, v in attrs:
                if n == "class" and v == "findList":
                    self._table = True
        elif tag == "td" and self._table:
            for n, v in attrs:
                if n == "class" and v == "result_text":
                    self._td = True
        elif tag == "a" and self._td:
            for n, v in attrs:
                if n == "href":
                    self._url = v.split("?")[0]
                    self._a = True
    
    def handle_data(self, data):
        data = data.strip()
        if data:
            if self._a:
                self._name = data
            elif self._td:
                self._name += " " + data
    
    def handle_endtag(self, tag):
        if tag == "a" and self._a:
            self._a = False
        elif tag == "td" and self._td:
            if self._name and self._url:
                self.list.append((self._name, self._url))
            self._name = ""
            self._url = ""
            self._td = False
        elif tag == "table" and self._table:
            raise StopParsing()


class KinopoiskSearchParser(BaseSearch):
    def __init__(self):
        super().__init__()
        self._p = False
        self._a = False
    
    def handle_starttag(self, tag, attrs):
        if tag == "p":
            for n, v in attrs:
                if n == "class" and v == "name":
                    self._p = True
        elif tag == "a" and self._p:
            for n, v in attrs:
                if n == "data-url" and "film" in v:
                    self._url = v + "/"
                    self._a = True
        elif tag == "div":
            for n, v in attrs:
                if "search_results_last" in v:
                    raise StopParsing()
    
    def handle_data(self, data):
        data = data.strip()
        if data:
            if self._a:
                self._name = data
            elif self._p:
                self._name += " (" + data + ")"
    
    def handle_endtag(self, tag):
        if tag == "a" and self._a:
            self._a = False
        elif tag == "p" and self._p:
            self._p = False
            if self._name and self._url:
                self.list.append((self._name, self._url))
                self._name = ""
                self._url = ""
