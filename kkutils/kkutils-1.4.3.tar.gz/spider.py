#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: zhangkai@cmcm.com
Last modified: 2018-01-05 17:21:17
'''
import asyncio
import collections
import copy
import hashlib
import inspect
import json
import pickle
import sys
import urllib.parse
from asyncio import Queue
from asyncio.locks import Lock
from concurrent.futures._base import CancelledError
from functools import partial
from importlib import import_module
from inspect import isclass
from signal import SIGINT, SIGTERM

import pyppeteer
import uvloop
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils import (AioPika, AioQueue, AioRedis, Config, Dict, Logger, Redis,
                   Request, Response)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def sched(trigger, **trigger_kwargs):
    def wrapper(func):
        func._trigger = trigger
        func._trigger_kwargs = trigger_kwargs
        return func
    return wrapper


class BaseChecker:

    def __init__(self, prefix='spider', retries=3):
        self.retries = retries
        self.lock = Lock()

    def __getattr__(self, key):
        def func(*args, **kwargs):
            return False
        return func

    async def __call__(self, key):
        with await self.lock:
            if self.check('succeed', key) or self.check('failed', key) or self.check('running', key):
                return False
            elif self.incr(key) < self.retries:
                self.add('running', key)
                return True
            else:
                self.add('failed', key)
                return False


class MemoryChecker(BaseChecker):

    def __init__(self, prefix='spider', retries=3):
        super().__init__(prefix, retries)
        self.cache = collections.defaultdict(int)
        self.storage = collections.defaultdict(set)

    def incr(self, key):
        self.cache[key] += 1
        return self.cache[key]

    def add(self, name, key):
        self.storage[name].add(key)

    def remove(self, name, key):
        if key in self.storage[name]:
            self.storage[name].remove(key)

    def check(self, name, key):
        return key in self.storage[name]


class RedisChecker(BaseChecker):

    def __init__(self, prefix='spider', retries=3):
        super().__init__(prefix, retries)
        self.prefix = prefix
        self.rd = Redis()

    def incr(self, key):
        return self.rd.hincrby(f'{self.prefix}_cache', key, 1)

    def add(self, name, key):
        self.rd.sadd(f'{self.prefix}_{name}', key)

    def remove(self, name, key):
        self.rd.srem(f'{self.prefix}_{name}', key)

    def check(self, name, key):
        return self.rd.sismember(f'{self.prefix}_{name}', key)


class QueueBroker:

    def __init__(self, prefix):
        self.queue = AioQueue() if prefix == 'unique' else Queue()

    async def get(self):
        return await self.queue.get()

    async def ack(self):
        self.queue.task_done()

    async def put(self, msg):
        return await self.queue.put(msg)

    async def size(self):
        return self.queue.qsize()

    async def join(self):
        await self.queue.join()

    async def finish(self):
        while not self.queue.empty():
            await self.queue.get()


class RedisBroker:

    def __init__(self, prefix):
        self.prefix = prefix
        self.queue = f'{self.prefix}_queue'
        self.running = f'{self.prefix}_running'
        self.rd = AioRedis(decode_responses=False)

    async def get(self):
        return await self.rd.brpoplpush(self.queue, self.running)

    async def ack(self):
        await self.rd.lpop(self.running)

    async def put(self, msg):
        await self.rd.lpush(self.queue, msg)

    async def size(self):
        return await self.rd.llen(self.queue) + await self.rd.llen(self.running)

    async def join(self):
        while await self.size():
            await asyncio.sleep(1)

    async def finish(self):
        pass


class AmqpBroker:

    def __init__(self, prefix):
        self.mq = AioPika(queue=prefix)

    async def get(self):
        return await self.mq.get()

    async def size(self):
        return await self.mq.size()

    async def ack(self):
        pass

    async def put(self, msg):
        await self.mq.publish(msg)

    async def join(self):
        while await self.size():
            await asyncio.sleep(1)

    async def finish(self):
        pass


class SpiderMeta(type):

    def __new__(cls, name, bases, attrs):
        sched_jobs = []
        for job in attrs.values():
            if inspect.isfunction(job) and getattr(job, '_trigger', None):
                sched_jobs.append(job)
        newcls = type.__new__(cls, name, bases, attrs)
        newcls._sched_jobs = sched_jobs
        return newcls


class Spider(metaclass=SpiderMeta):

    urls = ['https://www.baidu.com']

    def __init__(self, **kwargs):
        ''' opt params:
        splash: http://localhost:8050/render.html
        chrome: ws://localhost:3000
        broker: redis://localhost:6379
        '''
        module = sys.modules[__name__]
        self.opt = Dict(kwargs)
        self.logger = Logger(name='tornado.application')
        self.logger.info(json.dumps(self.opt, indent=4))
        self.http = Request(lib='tornado', max_clients=self.opt.workers, timeout=self.opt.timeout)
        self.broker = getattr(module, self.opt.broker)(self.opt.prefix)
        self.checker = getattr(module, self.opt.checker)(self.opt.prefix, self.opt.retries)
        self.sched = AsyncIOScheduler()
        self.loop = asyncio.get_event_loop()
        if hasattr(self, 'init'):
            ret = self.init()
            if inspect.isawaitable(ret):
                self.loop.run_until_complete(ret)
        if self.opt.chrome:
            self.loop.run_until_complete(self.launch())

    async def launch(self):
        self.browser = await pyppeteer.connect({'browserWSEndpoint': self.opt.chrome})
        self.page = await self.browser.newPage()

    async def close(self):
        await self.browser.close()

    def validate(self, url):
        return True

    async def crawl(self, url, callback, *args, **kwargs):
        ret = self.validate(url)
        if inspect.isawaitable(ret):
            ret = await ret
        if ret:
            msg = pickle.dumps((url, callback.__name__, args, kwargs))
            key = hashlib.md5(msg).hexdigest()
            if await self.checker(key):
                await self.broker.put(msg)

    async def parse(self, resp):
        self.logger.info(f'{resp.code}: {resp.url}')

    # @sched('interval', seconds=3)
    async def producer(self):
        for url in self.urls:
            await self.crawl(url, self.parse)

    async def process(self, msg):
        url, callback, args, kwargs = pickle.loads(msg)
        callback = getattr(self, callback)
        key = hashlib.md5(msg).hexdigest()
        data = copy.deepcopy(kwargs)
        splash = data.pop('splash', False)
        chrome = data.pop('chrome', False)
        if splash and self.opt.splash:
            data['url'] = url
            data.setdefault('http_method', data.pop('method', 'GET'))
            data.setdefault('wait', 1)
            if 'lua_source' in data:
                ret = urllib.parse.urlparse(self.opt.splash)
                splash_url = f'{ret.scheme}://{ret.netloc}/execute'
                resp = await self.http.post(splash_url, data=data, json=True)
            else:
                resp = await self.http.post(self.opt.splash, data=data, json=True)
        elif chrome and self.opt.chrome:
            render = data.pop('render', False)
            if render:
                try:
                    params = data.pop('params', {})
                    url += '?' + urllib.parse.urlencode(params)
                    await self.page.goto(url)
                    resp = Response(url=url, code=200)
                    resp.text = await self.page.content()
                    resp.body = resp.text.encode()
                except Exception as e:
                    self.logger.error(f'{url}: {e}')
                    resp = Response(url=url, code=599)
            else:
                resp = await self.http.request(url, **data)
                await self.page.setContent(resp.text)
                resp.text = await self.page.content()
                resp.body = resp.text.encode()
        else:
            resp = await self.http.request(url, **data)

        size = await self.broker.size()
        message = f'queue: {size}, url: {url} {resp.code} {resp.reason}'
        if 200 <= resp.code < 300:
            self.logger.info(message)
        else:
            self.logger.warning(message)

        codes = data.get('codes', ['200-299'])
        hit = False
        for code in codes:
            if isinstance(code, str) and int(code.split('-')[0]) <= resp.code <= int(code.split('-')[1]) or \
                    isinstance(code, int) and resp.code == code:
                hit = True
        self.checker.remove('running', key)
        succeed = False
        if hit:
            try:
                resp.meta = data
                ret = callback(resp, *args)
                if inspect.isawaitable(ret):
                    ret = await ret
                self.checker.add('succeed', key)
                succeed = True
            except Exception as e:
                self.logger.exception(e)

        if not succeed and not self._sched_jobs:
            await self.crawl(url, callback, *args, **kwargs)

    async def consumer(self):
        while True:
            try:
                msg = await self.broker.get()
                if self.opt.sleep:
                    await asyncio.sleep(self.opt.sleep)
                await self.process(msg)
                await self.broker.ack()
            except CancelledError:
                return self.logger.error('Cancelled consumer')
            except Exception as e:
                self.logger.exception(e)
                self.broker.ack()

    async def shutdown(self, sig):
        self.logger.warning(f'caught signal {sig.name}')
        await self.broker.finish()
        tasks = list(filter(lambda task: task is not asyncio.tasks.Task.current_task(), asyncio.Task.all_tasks()))
        self.logger.info(f'cancell tasks: {len(tasks)}')
        list(map(lambda task: task.cancel(), tasks))
        self.loop.stop()

    def start(self):
        for sig in (SIGINT, SIGTERM):
            self.loop.add_signal_handler(sig, partial(self.loop.create_task, self.shutdown(sig)))

        if 'consumer' in self.opt.roles:
            for _ in range(self.opt.workers):
                self.loop.create_task(self.consumer())

        if self._sched_jobs:
            self.checker = BaseChecker()
            self.logger.info(self._sched_jobs)
            for func in self._sched_jobs:
                function = func.__get__(self, self.__class__)
                self.sched.add_job(function, func._trigger, **func._trigger_kwargs)
                ret = function()
                if inspect.isawaitable(ret):
                    self.loop.create_task(ret)
            self.sched.start()
            self.loop.run_forever()
        elif self.opt.forever:
            if 'producer' in self.opt.roles:
                self.loop.create_task(self.producer())
            self.loop.run_forever()
        else:
            if 'producer' in self.opt.roles:
                self.loop.run_until_complete(self.producer())
            if 'consumer' in self.opt.roles:
                self.loop.run_until_complete(self.broker.join())
            if self.opt.chrome:
                self.loop.run_until_complete(self.close())
            if hasattr(self, 'finish'):
                ret = self.finish()
                if inspect.isawaitable(ret):
                    self.loop.run_until_complete(ret)


def main():
    opt = Config(dict(
        workers=10,
        timeout=10,
        retries=3,
        sleep=0,
        prefix='spider',
        checker='MemoryChecker',
        broker='QueueBroker',
        roles=['producer', 'consumer'],
        forever=False,
    ))
    arr = sys.argv[1].split('.')
    module = import_module(arr[0])
    if len(arr) == 1:
        for k, v in module.__dict__.items():
            if not k.startswith('__') and isclass(v) and any([x.__module__ == 'processor' and x.__name__ == 'Processor' for x in v.__bases__]):
                app = v(**opt)
                app.start()
    else:
        app = getattr(module, arr[1])(**opt)
        app.start()


if __name__ == '__main__':
    main()
