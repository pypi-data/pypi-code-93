import json
import time
from collections import Iterable
from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.spiders import Spider
from spider_core.serverapi import ServerApi
import six
from . import logger


def bytes_to_str(s, encoding='utf-8'):
    """Returns a str if a bytes object is given."""
    if six.PY3 and isinstance(s, bytes):
        return s.decode(encoding)
    return s


class HttpSpider(Spider):
    def __init__(self, instance_id, spider_id=None, **kwargs):
        super(HttpSpider, self).__init__()
        self.api = ServerApi(
            spider_id=spider_id,
            instance_id=instance_id,
        )
        self.redis_key = ''
        self.idle_count = 0
        self.item_list = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        obj = super(HttpSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(obj.spider_idle, signal=signals.spider_idle)
        crawler.signals.connect(obj.item_scraped, signal=signals.item_scraped)
        return obj

    def start_requests(self):
        return self.next_requests()

    def item_scraped(self, item, response, spider):
        """
        当item被爬取，并通过所有 Item Pipeline 后(没有被丢弃(dropped)，发送该信号
        :param item:
        :param response:
        :param spider:
        :return:
        """
        """可以根据shop_id实现 当前店铺采集的item数量"""
        if item:
            self.item_list.append(time.time())  # 每次触发 spider_idle时，记录下触发时间戳
            self.idle_count = 0
            # 判断 当前触发时间与上次触发时间 之间的间隔是否大于20秒，如果大于20秒则发送心跳包
            if (self.item_list[-1] - self.item_list[0]) > 20:
                self.item_list = [self.item_list[-1]]
                self.api.send_heartbeat(status='working')

    def fetch_data(self):
        datas = []
        for i in range(1):
            data = self.api.get_data(self.redis_key)
            if data and data['code'] == 200:
                datas.append(json.loads(data['data']))
            else:
                break
        return datas

    def next_requests(self):
        """Returns a request to be scheduled or none."""
        found = 0
        datas = self.fetch_data()
        for data in datas:
            reqs = self.make_request_from_data(data)
            if isinstance(reqs, Iterable):
                for req in reqs:
                    yield req
                    # XXX: should be here?
                    found += 1
                    logger.info(f'start req url:{req.url}')
            elif reqs:
                yield reqs
                found += 1
            else:
                logger.debug("Request not made from data: %r", data)

    def make_request_from_data(self, data):
        url = bytes_to_str(data)
        return self.make_requests_from_url(url)

    def schedule_next_requests(self):
        """Schedules a request if available"""
        # TODO: While there is capacity, schedule a batch of redis requests.
        for req in self.next_requests():
            self.crawler.engine.crawl(req, spider=self)

    def spider_idle(self, spider):
        """Schedules a request if available, otherwise waits."""
        self.schedule_next_requests()
        task_status = self.api.task_query()
        # logging.error(f'spider_idle---- task_status {task_status}')
        """向爬虫中台获取任务"""
        if task_status['code'] == 200:
            if task_status['data']['data_list_key']:
                redis_key = task_status['data']['data_list_key']
                self.api.task_id = task_status['data']['task_id']
                self.api.data_type = task_status['data']['data_type']
                self.redis_key = redis_key
                self.api.redis_key = redis_key

        """闲置状态 触发5次 发送心跳接口"""
        if self.idle_count == 5:
            self.api.send_heartbeat(status='waiting')
            # logging.error('send_heartbeat --- waiting')
            self.idle_count = 0
        self.idle_count += 1
        raise DontCloseSpider
