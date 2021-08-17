import urllib.request
from abc import ABC
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import tempfile
import concurrent.futures
import os


class TempHandler:
    def __init__(self, path=None):
        self.temp = os.path.join(
            os.path.dirname(__file__) if not path else path if os.path.isdir(path) else os.path.dirname(path),
            "temp"
        )

        None if os.path.exists(self.temp) else os.mkdir(self.temp)

    def __call__(self, is_dir=False, suffix='', prefix='', dir_=None, text=True):
        dir_ = dir_ if dir_ else self.temp

        if is_dir:
            path = tempfile.mkdtemp(suffix, prefix, dir_)
        else:
            mode, path = tempfile.mkstemp(suffix, prefix, dir_, text)
            os.close(mode)

        return path


class RepoSpider(CrawlSpider, ABC):
    name = 'Repo'
    allowed_domains = ['github.com']

    # using DEPTH FIRST ORDER

    rules = (
        Rule(
            LinkExtractor(
                restrict_xpaths="//div[@role='row']/div[@role='rowheader']/span/a",
                deny_extensions=set()  # allows any file
            ),
            callback='parse_item', follow=True, process_request="req_check"
        ),
    )

    def __init__(
            self,
            pipe,
            url,
            path

    ):
        super().__init__()
        self.start_urls = url

        self.pointer = path

        self.manager = concurrent.futures.ThreadPoolExecutor(
            max_workers=min(32, os.cpu_count() + 4),
            thread_name_prefix="Downloads"
        )

        self.pipe = pipe

    def start_requests(self):
        yield scrapy.Request(
            self.start_urls, errback=self.pipe_error, meta={"parent": self.pointer}
        )

    def pipe_error(self, reason):
        self.pipe["result"] = ""
        self.pipe["failed"] = True
        self.pipe["exception"] = str(reason)

    def req_check(self, request, response):
        self.logger.info(response.request.meta)

        request.meta["parent"] = response.request.meta["parent"]
        request.errback = self.pipe_error

        return request

    def parse_item(self, response):
        is_file = response.xpath("//div[@class='BtnGroup']/a[1]/@href").get()
        raw = response.urljoin(is_file)

        path = os.path.join(
            response.request.meta["parent"],
            os.path.split(raw)[-1]
        )

        self.manager.submit(self.download, raw, path) if is_file else os.mkdir(path)

        response.request.meta["parent"] = path

        yield {
            "is_file": is_file,
            "raw": raw,
            "path": path
        }

    def download(self, from_, to_):
        self.logger.info("Downloading %s", from_)
        return urllib.request.urlretrieve(from_, to_)

    def close(self, spider, reason):
        self.manager.shutdown(wait=True)  # may cause deadlock or may take forever
        # solved by killing the process if necessary

        self.pipe["result"] = self.pointer
        self.pipe["failed"] = False
        self.pipe["exception"] = ""

        super().close(spider, reason)
