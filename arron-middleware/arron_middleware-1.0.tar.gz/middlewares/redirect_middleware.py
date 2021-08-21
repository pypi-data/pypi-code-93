"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/8/21 下午6:42
"""
import logging
from scrapy.exceptions import IgnoreRequest
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.redirect import BaseRedirectMiddleware
from w3lib.url import safe_url_string
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class CustomRedirectMiddleware(BaseRedirectMiddleware, RetryMiddleware):
    def __init__(self, crawler):
        super(CustomRedirectMiddleware, self).__init__(crawler.settings)
        self.max_retry_times = crawler.settings.getint('RETRY_TIMES')
        self.priority_adjust = crawler.settings.getint('RETRY_PRIORITY_ADJUST')
        self.stats = crawler.stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        if (request.meta.get('dont_redirect', False) or
                response.status in getattr(spider, 'handle_httpstatus_list', []) or
                response.status in request.meta.get('handle_httpstatus_list', []) or
                request.meta.get('handle_httpstatus_all', False)):
            return response

        allowed_status = (301, 302, 303, 307, 308)
        if 'Location' not in response.headers or response.status not in allowed_status:
            return response

        location = safe_url_string(response.headers['Location'])
        if response.headers['Location'].startswith(b'//'):
            request_scheme = urlparse(request.url).scheme
            location = request_scheme + '://' + location.lstrip('/')

        redirected_url = urljoin(request.url, location)

        if 'check' in redirected_url or 'wappass.baidu.com/static/captcha' in redirected_url\
                or 'fs/forbid' in redirected_url:
            self.stats.inc_value('redirect')
            logger.warning('跳转到登录页面, 重试')  # 使用原来的地址请求重试
            logger.debug('跳转状态: %s, 跳转url: %s', response.status, redirected_url)
            req = self._retry(request, "跳转到登录页面", spider)
            if req is not None:
                return req
            else:
                raise IgnoreRequest

        if response.status in (301, 307, 308) or request.method == 'HEAD':
            redirected = request.replace(url=redirected_url)
            return self._redirect(redirected, request, spider, response.status)

        redirected = self._redirect_request_using_get(request, redirected_url)
        return self._redirect(redirected, request, spider, response.status)

