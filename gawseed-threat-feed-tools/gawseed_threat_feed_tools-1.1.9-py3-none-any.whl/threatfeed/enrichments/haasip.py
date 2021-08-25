from gawseed.threatfeed.enrichments import Enrichment

class HAASIPEnrichment(Enrichment):
    def __init__(self, conf):
        super().__init__(conf)
        self.require(['url'])

        self._url = self.config('url')
        self._tag = self.config('tag')

    def type():
        return 'application/json'

    def gather(self, key, extra_info):
        return self.geturl(self._url.format(tag=self._tag, key=key)
