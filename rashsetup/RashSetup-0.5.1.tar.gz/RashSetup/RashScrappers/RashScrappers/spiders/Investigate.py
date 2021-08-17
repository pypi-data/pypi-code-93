import scrapy


class Investigator(scrapy.Spider):
    name = 'Settings'
    allowed_domains = [
        'github.com'
    ]

    def __init__(
            self,
            pipe,
            url

    ):
        super().__init__(Investigator.name)
        self.start_urls = url
        self.pipe: dict = pipe
        self.is_py = [False, False]

    def start_requests(self):
        yield scrapy.Request(
            self.start_urls, errback=self.pipe_error
        )

    def pipe_error(self, reason):
        self.pipe["result"] = ""
        self.pipe["failed"] = True
        self.pipe["exception"] = str(reason)

    def parse(self, response, *args):
        entities = response.xpath("//div[@class='Box-row Box-row--focus-gray py-2 d-flex position-relative "
                                  "js-navigation-item ']")

        candi = (
            "__init__.py", "settings.json"
        )

        for entity in entities:
            name = entity.xpath(".//span/a/text()").get()
            token = candi.index(name) if name in candi else 2

            if token == 0:
                self.is_py[0] = True
                yield {
                    "status": "Found __init__.py hence, Valid Python Module"
                }

            elif token == 1:
                self.is_py[1] = True
                yield scrapy.Request(
                    response.urljoin(
                        entity.xpath(".//span/a/@href").get()
                    ), callback=self.yield_raw, errback=self.pipe_error, meta={"name": name}
                )

    def yield_raw(self, response):
        raw = response.urljoin(response.xpath("//div[@class='BtnGroup']/a/@href").get())

        self.pipe["result"] = raw

        yield {
            "name": response.request.meta["name"],
            "raw_link": raw
        }

    def close(self, spider, reason):
        self.pipe["failed"] = not all(self.is_py)

        if self.pipe["failed"]:
            self.pipe["exception"] = "Not a Valid Python Module" if self.is_py.index(
                False) == 0 else "Missing Settings.json"
        else:
            self.pipe["exception"] = ""
        return super().close(spider, reason)
