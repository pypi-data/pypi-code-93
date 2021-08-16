#!/usr/bin/env python3
"""Lookup words on wikipedia and print their extract."""

# pylint: disable=R0201
# pylint: disable=R0911
# pylint: disable=R1705
# broken:
# pyright: reportGeneralTypeIssues=warning

import argparse
import json
import multiprocessing
import multiprocessing.pool
import os
import subprocess
import sys
import typing
from urllib.parse import quote_plus

import requests
import termcolor
from pyfzf.pyfzf import FzfPrompt

from .models import DisambiguationPage, MainPage, Page, StandardArticle

SUMMARY_API = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{word}"
API_URL = "https://{lang}.wikipedia.org/w/api.php"
SEARCH_ENGINE = "https://ddg.co/?q={query}"
LANGS = ["de", "en"]


class Wiki:
    """Cli class."""

    def __init__(self, word: str, langs: typing.List[str]):
        self.session = requests.Session()
        self.word = word
        self.langs = langs
        self.pool = multiprocessing.pool.ThreadPool(
            max(multiprocessing.cpu_count() - 2, len(self.langs))
        )

    def run(self):
        """Run lookups in multiple languages in parallel."""
        results = self.pool.map(self.lookup, self.langs)
        self.pool.close()
        self.pool.join()
        errs: list[Exception] = [res for res in results if isinstance(res, Exception)]
        res: list[Page] = [res for res in results if isinstance(res, Page)]

        if errs:
            termcolor.cprint("There have been errors:", color="red")

            for err in errs:
                termcolor.cprint(str(err), color="yellow", file=sys.stderr)

            sys.exit(1)

        if not res:
            termcolor.cprint(
                "Nothing found", color="red", attrs=["italic"], file=sys.stderr
            )

            while True:
                response = input(
                    termcolor.colored(
                        "Do you want to search for that term? [Yn] ",
                        color="yellow",
                        attrs=["italic"],
                    )
                ).strip()

                if not response:
                    response = "y"

                if response.lower() in ("y", "n"):
                    break

            if response.lower() == "y":
                query = quote_plus(self.word)
                # pylint: disable=consider-using-with
                subprocess.Popen(
                    ("xdg-open", SEARCH_ENGINE.format(query=query)),
                    stdin=None,
                    stdout=None,
                    stderr=None,
                    close_fds=True,
                )
                sys.exit(0)

            sys.exit(1)
        else:
            article: Page = res[0]
            print(article.format())

        if isinstance(article, DisambiguationPage):
            self.ask_disambiguation(article.title, article.lang)

    def ask_disambiguation(self, title: str, lang: str):
        """Clearify disambiguation."""
        # get links
        links = self.get_links_of_page(
            title=title,
            lang=lang,
        )
        print("\n\n")

        # ask which link we want to follow
        termcolor.cprint(
            "This page is a disambiguation page. Do you want to follow a link?",
            color="green",
            attrs=["bold"],
        )
        fzf = FzfPrompt()
        try:
            title = fzf.prompt(links, "--height=10")[0]
        except Exception as exc:  # pylint: disable=W0703
            print(exc, file=sys.stderr)
            sys.exit(1)

        # run again
        print("\n\n")
        wiki = Wiki(title, self.langs)
        wiki.run()

    def _make_api_get_request(self, **kwargs) -> typing.Any:
        """Make get request and return json data."""
        response = self.session.get(**kwargs)
        response.raise_for_status()
        data = response.json()

        return data

    def lookup(self, lang: str) -> typing.Union[Page, Exception, None]:
        """Lookup the word in ``lang``."""
        try:
            data = self._make_api_get_request(
                url=SUMMARY_API.format(lang=lang, word=self.word)
            )
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                return None
            else:
                return err
        except json.JSONDecodeError as err:
            return err

        try:
            title = data["title"]
            link = data["content_urls"]["desktop"]["page"]

            if data["type"] in "standard":
                try:
                    img_url = data["thumbnail"]["source"]
                    img = self.get_img(img_url)
                except KeyError:
                    img = None

                return StandardArticle(
                    lang=lang,
                    title=title,
                    link=link,
                    image=img,
                    extract_html=data["extract_html"],
                )
                #  self.format_standard_article(data), data["type"]
            elif data["type"] == "disambiguation":
                return DisambiguationPage(
                    lang=lang,
                    title=title,
                    link=link,
                    extract_html=data["extract_html"],
                )
                #  return self.format_disambiguation_article(data), data["type"]
            elif data["type"] == "mainpage":
                return MainPage(
                    lang=lang,
                    title=title,
                    link=link,
                )
                #  return self.format_mainpage_article(data), data["type"]
            else:
                return ValueError(f'Unknown article type {data["type"]}')
        except KeyError as err:
            return err

    def get_links_of_page(self, title: str, lang: str) -> list[str]:
        """Query all links on a page."""
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "links",
            "pllimit": "max",
        }
        api_url = API_URL.format(lang=lang)
        pg_count = 0
        page_titles = []

        try:
            while True:
                try:
                    data = self._make_api_get_request(url=api_url, params=params)
                except requests.exceptions.HTTPError as err:
                    print(err, file=sys.stderr)
                    sys.exit(1)
                except json.JSONDecodeError as err:
                    print(err, file=sys.stderr)
                    sys.exit(1)

                pages = data["query"]["pages"]
                pg_count += 1

                for _page_id, val in pages.items():
                    for link in val["links"]:
                        if link["ns"] == 0:
                            page_titles.append(link["title"])

                if "continue" not in data:
                    break

                plcontinue = data["continue"]["plcontinue"]
                params["plcontinue"] = plcontinue

        except KeyError as err:
            print(err, file=sys.stderr)
            sys.exit(1)

        return page_titles

    def get_img(self, img_url: str) -> typing.Optional[str]:
        """Download image from wikipedia and convert it to term string."""
        ret = self.session.get(img_url)
        try:
            ret.raise_for_status()
        except requests.exceptions.HTTPError:
            #  print('Could not fetch image', err)

            return None

        try:
            img_height = (os.get_terminal_size().lines - 15) * 2
        except OSError:
            img_height = 50

        try:
            with subprocess.Popen(
                ["catimg", "-H", str(img_height), "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            ) as proc:
                stdout, stderr = proc.communicate(input=ret.content)

        except subprocess.CalledProcessError as err:
            print(err, file=sys.stderr)

            return None

        if stderr and stderr.strip():
            print(stderr.strip(), file=sys.stderr)

            return None

        return stdout.decode(sys.stdout.encoding)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "term",
        nargs="+",
        type=str,
        action="extend",
        help="The term to look-up.",
    )
    parser.add_argument(
        "-l",
        "--lang",
        action="append",
        type=str,
        choices=LANGS,
        help="The languages to look-up. Order will be respected.",
    )
    args = parser.parse_args()
    args.term = " ".join(args.term)
    args.lang = args.lang if args.lang else LANGS

    return args


def main():
    """Do it."""
    # hack termcolor
    termcolor.ATTRIBUTES["italic"] = 3  # noqa
    # parse command line args
    args = parse_args()
    # run
    wiki = Wiki(args.term, args.lang)
    wiki.run()


if __name__ == "__main__":
    main()
