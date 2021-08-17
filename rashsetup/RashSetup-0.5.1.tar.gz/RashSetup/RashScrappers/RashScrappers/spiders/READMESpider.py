import scrapy


class READMESpider(scrapy.Spider):
    name = 'READMESpider'

    def __init__(
            self,
            pipe,
            url
         ):
        super().__init__(READMESpider.name)

        self.pipe = pipe
        self.start_urls = url

    def start_requests(self):
        yield scrapy.Request(
            self.start_urls, errback=self.pipe_error
        )

    def pipe_error(self, reason):
        self.pipe["result"] = ""
        self.pipe["failed"] = True
        self.pipe["exception"] = str(reason)

    def parse(self, response, *_):
        self.pipe["result"] = response.xpath("//div[@id='readme']").extract_first()

        yield {
            "status": f"Extracted README from {response.request.url}"
        }

    def close(self, spider, reason):
        self.pipe["failed"] = not bool(self.pipe["result"])

        super().close(spider, reason)


