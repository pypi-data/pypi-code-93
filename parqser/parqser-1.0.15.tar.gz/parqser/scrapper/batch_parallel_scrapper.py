from typing import List
from itertools import islice, chain
import threading
from time import sleep
from loguru import logger
from parqser.scrapper import BaseScrapper
from parqser.page import DownloadState, LoadedPage
from parqser.session import BaseSession, EmptySession


class DownloadThread(threading.Thread):
    def __init__(self, url: str, session: BaseSession):
        self.session = session
        self.url = url
        self.result = None
        threading.Thread.__init__(self)

    def _load_page(self, url: str, session: BaseSession):
        try:
            res = session.get(url)
            state = DownloadState.OK
        except Exception as e:
            state = DownloadState.FAILED
            logger.error(f"Unexpected {e} accured on url {url}")
            res = ""
        self.page = LoadedPage(res.text, state)

    def run(self):
        self._load_page(self.url, self.session)


class BatchParallelScrapper(BaseScrapper):
    def __init__(self, n_jobs=1, interval_ms=1000, sessions: List[BaseSession] = []):
        self.n_jobs = n_jobs
        self.interval_ms = interval_ms
        self.sessions = self._make_sessions(sessions)

    def _make_sessions(self, sessions: List[BaseSession]) -> List[BaseSession]:
        """Validates sessions objects"""
        is_session = lambda sess: isinstance(sess, BaseSession)
        if len(sessions) == 0:
            sessions = [EmptySession() for _ in range(self.n_jobs)]
        elif len(sessions) != self.n_jobs:
            raise AttributeError('length of sessions should be same as n_jobs or zero')
        elif not all(map(is_session, sessions)):
            raise AttributeError('all sessions should be isnstances of requests.Session')
        return sessions

    def batch_urls(self, urls: list):
        """Batch iterator"""
        try:
            it = iter(urls)
            while True:
                bi = islice(it, self.n_jobs)
                yield list(chain([bi.__next__()], bi))
        except StopIteration:
            return

    def load_pages(self, urls: List[str]) -> List[LoadedPage]:
        threads = [DownloadThread(url, session) for url, session in zip(urls, self.sessions)]
        [t.start() for t in threads]
        [t.join() for t in threads]

        pages = [t.page for t in threads]
        return pages

    def wait(self):
        # TODO: elapsed timers
        sleep(self.interval_ms / 1000)
