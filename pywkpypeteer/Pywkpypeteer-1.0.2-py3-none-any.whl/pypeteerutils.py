#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from pyppeteer import launch
from pywkmisc import DateUtils

from typing import Union


class PetRunError(RuntimeError):
    def __init__(self, arg):
        self.args = arg
"""
    @staticmethod
    def screenSize(is_mobile):
        if is_mobile:
            return 375, 812
        else:
            return 1080, 768
"""
_default_config = {
    "width": 1080,
    "height": 768,
    "timeout": 1000 * 60 * 5, #五分钟
    "mobile_width": 375,
    "mobile_height": 812,
    "ismobile": False,
    "emulate": {
        'userAgent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) '
                     'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                     'Version/13.0.3 Mobile/15E148 Safari/604.1',
        'viewport': {
            "width": 375,
            "height": 812,
            "isMobile": True,
            "hasTouch": True
        }
    },
    "launch": {
        'headless': False,
        'dumpio': True,
        #'devtools': True,
        "args": [
            "--start-maximized",
            "--no-sandbox",
            "--disable-infobars"
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--ignore-certificate-errors',
            '--hide-scrollbars',
            '--disable-bundled-ppapi-flash',
            '--disable-infobars'
        ]
    },
    "screenshot":{
        'ext': 'jpg',
        'type': 'jpeg',
        'quality': 50,
        'fullPage': True
    }
}


class PypeteerUtils(object):
    """
        网络爬虫
    """

    @staticmethod
    def default_config():
        return _default_config

    @staticmethod
    async def browder(config=None):
        global _default_config
        if config is not None:
            _default_config = config

        if _default_config['ismobile']:
            _default_config['width'] = _default_config['mobile_width']
            _default_config['height'] = _default_config['mobile_height']
        _default_config['launch']['args'].append(
            '--window-size={},{}'.format(_default_config['width'], _default_config['height'])
        )

        browser = await launch(_default_config['launch'])
        return browser

    @staticmethod
    async def page(browser=None):
        if browser is None:
            raise PetRunError('browser is None')
        pages = await browser.pages()
        if len(pages) > 0:
            page = pages[0]
        else:
            page = await PypeteerUtils.newPage(browser)
        return page

    @staticmethod
    async def newPage(browser):
        return await browser.newPage()

    @staticmethod
    async def emulate(page):
        global _default_config
        if _default_config['ismobile']:
            await page.emulate(_default_config['emulate'])
        else:
            await page.setViewport({
                "width": _default_config['width'],
                "height": _default_config['height']
            })

    @staticmethod
    async def open(page, url):
        await PypeteerUtils.emulate(page)
        # 本页刷新后值不变
        await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'
                                         '{ webdriver:{ get: () => false } }) }')
        await page.goto(url,{
            'timeout': _default_config['timeout']
        })
        # await page.waitForNavigation()
        await asyncio.sleep(2)
        if await page.evaluate('window.location.href') == 'chrome-error://':
            raise PetRunError('{}网页无法打开'.format(url))

        await PypeteerUtils.scrollPage(page, _default_config['height'])
        await asyncio.sleep(1)

    @staticmethod
    async def local(page):
        try:
            await page.goto('chrome-search://local-ntp/local-ntp.html')
            await asyncio.sleep(2)
        except Exception as e:
            print(e)

    @staticmethod
    async def spdierAd(page, url, adjs):
        await PypeteerUtils.open(page, url)
        ads = await page.evaluate(adjs)
        frames = page.frames
        for frame in frames:
            if frame.url == page.url:
                continue
            print('frame = {}'.format(frame.url))
            ads2 = await frame.evaluate(adjs)
            if ads2 is not None and len(ads2) > 0:
                ads += ads2
        screenshot_file = PypeteerUtils.screenshotFile(page)
        return screenshot_file, ads

    @staticmethod
    async def screenshotFile(page, screenshot_file=None) -> Union[bytes, str]:
        print('截图')
        if screenshot_file is None:
            screenshot_file = '{}.{}'.format(DateUtils.get_timestamp(),_default_config['screenshot']['ext'])
        await page.screenshot({
            'path': screenshot_file,
            'type': _default_config['screenshot']['type'],
            'quality': _default_config['screenshot']['quality'],
            'fullPage': _default_config['screenshot']['fullPage']
        })
        return screenshot_file

    @staticmethod
    async def scrollPage(page, screenheight):
        cur_dist = 0
        height = await page.evaluate("() => document.body.scrollHeight")
        num = 0
        while True:
            """ image max height 65500 ,scrollBy 50 page"""
            if cur_dist < height and num < 50:
                await page.evaluate("window.scrollBy(0, {});".format(screenheight))
                await asyncio.sleep(0.5)
                cur_dist += screenheight
                num += 1
                if await page.evaluate('document.images.length') > 0:
                    await page.waitForSelector('img')
                height = await page.evaluate("() => document.body.scrollHeight")
            else:
                break
        print('滚屏完毕')

    @staticmethod
    async def close(browser):
        await browser.close()

if __name__ == '__main__':
    # asyncio.get_event_loop().run_until_complete(main(False))
    pass
