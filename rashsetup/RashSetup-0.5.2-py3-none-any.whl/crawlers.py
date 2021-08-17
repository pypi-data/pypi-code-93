import queue
import typing
from .RashScrappers.RashScrappers.spiders import *
from .shared import *
import multiprocessing
import logging
import logging.handlers
import scrapy.crawler
from twisted.internet import reactor
import sys
import subprocess

ALL.extend(
    [
        "Setup",
        "READMERawSetup",
        "SettingsRawSetup",
        "RepoRawSetup",
        "TempHandler",
        "SettingsParser",
        "FullInvestigateRawSetup"
    ]
)

__all__ = ALL


class QueueHandler(logging.handlers.QueueHandler):
    def __init__(self, queue_: queue.Queue):
        super().__init__(queue_)

    def handle(self, record) -> bool:
        # to make this pickle-able
        # avoiding all lambda functions from scrapy logs

        modified = logging.LogRecord(
            record.name,
            record.levelno,
            record.pathname,
            record.lineno,
            record.getMessage(),
            args=(),
            exc_info=record.exc_info,
            func=record.funcName,
            sinfo=record.stack_info
        )

        return super().handle(modified)


class SettingsParser:
    def __init__(self, json_url: str):
        self.parsed = JsonHandler().parse_url(json_url)
        self.url = json_url

    def __getitem__(self, key: str) -> typing.Union["SettingsParser", bool, str]:
        if key == "result":
            return self

        elif key == "failed":
            return not self.validate()

        else:
            return "" if self.validate() else "exception"

    def __contains__(self, item: str) -> bool:
        return True  # assuming we check only for result, failed, exception keys
        # ! Assumed 100 % efficiency since this is one of a internal class

    def load(self):
        return self

    def close(self):
        pass

    def settings(self) -> str:
        return self.url

    def name(self) -> str:
        return self.parsed["name"]

    def version(self) -> str:
        return self.parsed["version"]

    def hosted(self) -> str:
        return self.parsed["hosted"]

    def readme(self) -> typing.Union[str, bool]:
        return self.parsed.get("readme", False)

    def desc(self) -> str:
        return self.parsed.get("desc", "A Rash Module")

    def required(self) -> typing.List[str]:
        return self.parsed.get("requires", [])

    def update_readme(self, raw: str) -> typing.NoReturn:
        self.parsed["readme"] = raw

    def validate(self) -> bool:
        required = (
            "name", "version", "hosted"
        )  # required

        return all(
            (
                _ in self.parsed for _ in required
            )
        )

    def install_required(self) -> typing.NoReturn:
        temp = TempHandler()(False, ".txt")

        with open(temp, 'w') as writer:
            writer.writelines(self.required())

        subprocess.run(
            [
                sys.executable, "-m", "pip", "install", '-r', temp
            ]
        )


class RawSetup:
    def __init__(self, pipe: typing.Any, log_pipe: typing.Optional[queue.Queue] = None, *args):
        self.pipe = pipe
        self.pipe.saved = None

        self.cache: typing.Dict[str, typing.Union[bool, str, None, SettingsParser]] = {
            "failed": True,
            "exception": "Failed before scrapping",
            "result": None
        }

        self.logger = logging.getLogger("")

        self.logger.addHandler(
            QueueHandler(log_pipe)
        ) if log_pipe else None

        self.start(*args)

    def start(
            self,
            spider: typing.Union[Investigator, RepoSpider, READMESpider],
            *args
    ) -> None:
        process = scrapy.crawler.CrawlerProcess()
        process.crawl(spider, self.cache, *args)
        process.start(True)

        self.save()

    def save(self) -> typing.NoReturn:
        handler = JsonHandler(
            TempHandler()(
                suffix=".json"
            )
        )

        handler.dump(self.cache)
        self.pipe.saved = handler

        self.logger.info("saved raw data into %s", handler.file)
        reactor.stop() if reactor.running else None


class READMERawSetup(RawSetup):
    def start(self, url: str, *_):
        super().start(READMESpider, url)


class SettingsRawSetup(RawSetup):
    def start(self, url: str, *_):
        super().start(Investigator, url)


class RepoRawSetup(RawSetup):
    def start(self, *args):
        super().start(RepoSpider, *args)


class FullInvestigateRawSetup(RawSetup):
    def __init__(self, *_, **__):
        self.temp = {}

        super().__init__(*_, **__)

    def start(self, url: str, *_):
        process = scrapy.crawler.CrawlerProcess()

        process.crawl(
            Investigator, self.cache, url
        ).addCallback(self.ask_readme)

        process.start(False)

    def ask_readme(self, _):
        if self.cache.get("failed", True) or not self.cache.get("result", ""):
            return self.save()

        sample = SettingsParser(self.cache["result"])

        if not sample.validate():
            return self.save()

        self.cache["result"] = sample

        process = scrapy.crawler.CrawlerProcess()

        process.crawl(
            READMESpider, self.temp, sample.readme()
        ).addCallback(self.save_readme)

    def save_readme(self, _):
        if self.temp.get("failed", True):
            return self.save()

        self.cache["result"].update_readme(self.temp["result"])
        self.temp.clear()

        self.save()

    def save(self):
        if self.cache["failed"]:
            return super().save()

        self.pipe.saved = self.cache["result"]
        reactor.stop() if reactor.running else None


class Setup:
    def __init__(
            self,
            target: typing.Union[RepoRawSetup, FullInvestigateRawSetup, READMERawSetup, SettingsRawSetup],
            *args,
            create: bool = True
    ):

        self._manager = multiprocessing.Manager()
        self.saved = self._manager.Namespace()

        self.url = args[0]  # url

        self._ = multiprocessing.Process(
            target=target, args=(
                self.saved, None, *args
            )
        ) if create else None

    def join(self, timeout: typing.Optional[int] = None):
        self._.join(timeout)

    def results(self) -> typing.Tuple[bool, typing.Union[SettingsParser, JsonHandler, str]]:
        """
        returns the result of a process that was saved inside "saved" attribute of multiprocessing.Manager().Namespace

        :return: passed[bool], result[typing.Any]
        """

        raw: JsonHandler = getattr(self.saved, "saved") if hasattr(self.saved, "saved") else None

        if not raw:
            return False, "Not a feasible result"

        loaded = raw.load()

        raw.close()
        self.close()

        if not all(("failed" in loaded, "result" in loaded, "exception" in loaded)):
            return False, "Missing Values"

        if loaded["failed"]:
            return False, loaded["exception"]

        return True, loaded["result"]

    def close(self):
        self._.close()

    def start(self):
        self._.start()
