"""
This is a simple selenium wrapper to make writing a browser bot easier
with builtin proxy support so it's easy to get request/response headers

Why this file name:
Tried browserbot, seleniumbot, webbot and they are taken as python librarys
The only reason I choose this name is it's short and not taken :D
"""

# pylint: disable=invalid-name
import json
import logging
import time
from functools import wraps

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement


log = logging.getLogger('wenbot')
def select(self, css, _filter=None):
    """calls find_elements_by_css_selector
    :_filter: if callable, return [i for i in elements if _filter(i)]
        normally filter can check for i.text for example
        if _filter is str, return [i for i in elements if i.text.strip() == _filter]
    Demo:
    ```
    arr = br.select('span.navBarTopLevelItem')
    DROPDOWN_MENUITEM = 'span.ms-crm-VS-MenuItem-Title'
    category='Activated Processes'
    bot.select(DROPDOWN_MENUITEM, category)
    ```
    """
    eles = self.find_elements_by_css_selector(css)
    if _filter is not None:
        if callable(_filter):
            res = [i for i in eles if _filter(i)]
        else:
            res = [i for i in eles if i.text.strip() == _filter]
        if not res:
            log.info(f'select not found "{_filter}" in {[i.text.strip() for i in eles]}')
        eles = res
    return eles


Chrome.select = select
WebElement.select = select


def play(self, action, *args):
    """ Play action or actions, see demo code:
    :param action: if it's a list/tuple, it should be a collection of actions.
        otherwise action can be 'open', 'text', 'click', 'wait'.
    when action='open', args = (url,)
        eg: ('open', 'https://www.google.com')
    when action='text', args = (css_selector, text, aux)
        if 'clear' in aux: clear textfield before input
        if 'enter' in aux: send enter key after input
    when action='click', args = (css_selector,)
    when action='wait', args = (seconds_to_sleep,)
    css_selector format:
        - string, as normal css selector
        - (string, int) to select nth element in the list of selected elements
    ```
    play_book_login = (
        ('text', 'input[name=loginfmt]', userid, 'clear'),
        ('click', 'input[type=submit]'),
        ('text', 'input[name=passwd]', passwd, 'clear'),
        ('wait', 1),
        ('click', 'input[type=submit]'),
        ('click', ('#sometable input', 3)), # click on 3rd input in that table
            # in this case '#sometable input:nth-of-type(3)' may not work
            # because the input elements may have different parents like td
            # so in css selector perspective, they are all 1st of its type
    )
    bot.play(play_book_login)
    ```
    """
    if not isinstance(action, str):
        for item in action:
            play(self, *item)
        return

    def find_element(_func):
        """find element by selector or skip f() if not found"""
        @wraps(_func)
        def wrap(selector, *args, **kw):
            nth = 0
            if isinstance(selector, (tuple, list)):
                selector, nth = selector
            ele = next(iter(self.select(selector)[nth:]), None)
            if not ele:
                log.warning(f'{_func.__name__} nothing for '
                      f'{repr(selector)} nth={nth}')
                return None
            return _func(ele, *args, **kw)
        return wrap

    def _open(url):  # goto url
        return self.get(url)

    @find_element
    def click(ele, aux=''):
        """click the element specified by css selector, see find_element()"""
        for _ in range(60):
            try:
                ele.click()
                return
            except Exception as exc:
                # selenium.common.exceptions.WebDriverException: Message: unknown error:
                # Element <div class="dropdown-group">...</div> is not clickable at point
                if 'clickable' in str(exc):
                    log.info(f'waiting for clickable {exc}')
                    time.sleep(1)
                    continue
                raise

    @find_element
    def text(ele, t, aux=''):  # input text in first element of css selector
        """send text to the element specified by css selector, see find_element()
        :param aux: 'clear,enter'"""
        if 'clear' in aux:
            ele.clear()
        if t:
            ele.send_keys(t)
        if 'enter' in aux:
            ele.send_keys(Keys.ENTER)

    def wait(n):  # wait n seconds
        time.sleep(n)
    actions = {'open': _open, 'click': click, 'text': text, 'wait': wait}
    action_func = actions.get(action)
    time.sleep(0.1)
    _ = action_func(
        *args) if action_func else log.info(f'illegal action {repr(action)} {repr(args)}')


Chrome.play = play


def body_html(self):
    """helper return html of body element"""
    return self.select('body')[0].html()


def body_soup(self):
    """helper return beautifulsoup object of current body_html"""
    import bs4
    return bs4.BeautifulSoup(body_html(self), 'html5lib')


Chrome.body_html = body_html
Chrome.body_soup = body_soup


# possible to eliminate (br the WebDrive obj) in argument using self._parent as discussed in
# https://groups.google.com/forum/#!topic/webdriver/Qtp4rVhiTUc

# customised left_shift_click(), double_click(), children() of all elements
def left_shift_click(self, br):
    """helper do left shift click on current element"""
    ActionChains(br).key_down(Keys.LEFT_SHIFT).click(
        self).key_up(Keys.LEFT_SHIFT).perform()
    # size = self.size  # {'height': 37, 'width': 302}
    # ac = ActionChains(br).key_down(Keys.LEFT_SHIFT).move_to_element(
    #     self).move_by_offset(-size['width']/2+10, 0).click().key_up(Keys.LEFT_SHIFT)
    log.info(
        f'left_shift_clicked on {self} {self.tag_name} {self.get_attribute("outerHTML")}')


def double_click(self, br):
    """ demo:
    # double click on every spacer to expand column width
    for spc in br.select('table.ms-crm-List-Header span.ms-crm-List-Row-header-spacer'):
        spc.double_click(br)
    """
    ActionChains(br).double_click(self).perform()


def children(self):
    """return all children elements"""
    return self.find_elements_by_xpath('*')


def html(self):
    """helper to return current element outerHTML"""
    return self.get_attribute('outerHTML')


WebElement.left_shift_click = left_shift_click
WebElement.double_click = double_click
WebElement.children = children
WebElement.html = html


""" demo of using frames
br.switch_to.frame('contentIFrame0')
# do select etc here
br.switch_to.parent_frame()  # switch back
"""


# https://github.com/lightbody/browsermob-proxy/releases
# requires java to run browsermob-proxy
browsermob_proxy_bin = 'browsermob-proxy-2.1.4/bin/browsermob-proxy'
proxy_server = [None]  # use list to bypass global var modification

# change default options


def proxy_new_har(func):
    """user can call new_har again to change options.
    Because proxy.har is a property and every access will trigger a requests.get,
    it's better to use new_har() to start a new set of har and return old set when it's possible.
    Then it's necessary to give proper default values to let calling new_har() more easier.
    """
    default_ref = 'har1'
    default_options = {
        'captureHeaders': True,
        'captureContent': False,
        'captureBinaryContent': False,
    }

    @wraps(func)
    def wrap(ref=None, options=None, title=None, **kwargs):
        return func(ref=ref or default_ref,
                    options=options or default_options,
                    title=title,
                    **kwargs)

    return wrap


def har_request_headers(har, offset=-1):
    """helper to return specified request headers for requests call"""
    return {i['name']: i['value'] for i in har['log']['entries'][offset]['request']['headers']}


def open_chrome(headless=True, proxy=False, window_size=(1920, 5000)):
    """helper to create Chrome object with proxy setup"""
    import atexit
    if proxy:
        if not proxy_server[0]:
            from browsermobproxy import Server
            proxy_server[0] = Server(browsermob_proxy_bin)
            proxy_server[0].start()
            atexit.register(
                lambda *args:
                (
                    proxy_server[0].stop(),
                    log.info(f'Browsermob-proxy server stopped {args}'),
                )
            )
        proxy = proxy_server[0].create_proxy()
        proxy.new_har = proxy_new_har(proxy.new_har)
        proxy.new_har()
        # new_har() returns (statuscode, har)

    options = ChromeOptions()
    options.add_argument('--disable-extensions')
    if proxy:
        options.add_argument(f'--proxy-server={proxy.proxy}')
    if headless:
        options.add_argument('headless')  # if headless
    # the following code doesn't work, just save for reference
    # prefs = {
    #     "plugins.plugins_list": [{
    #         "enabled": False,
    #         "name": "Chrome PDF Viewer"
    #     }],  # Disable Chrome's PDF Viewer
    #     "download.default_directory": '/tmp/',
    #     "download.extensions_to_open": "applications/pdf",
    # }
    # options.add_experimental_option("prefs", prefs)
    # === end of save code
    br = Chrome(options=options)
    # default is 0. wait before throw 'No Such Element'
    br.implicitly_wait(10)
    # self.br.maximize_window()
    if window_size:
        br.set_window_size(*window_size)
    br.proxy = proxy or None
    # it's safe to call quit multiple times so this is to make sure
    # normally there is only one instance anyway
    atexit.register(
        lambda *args:
        (
            br.quit(),
            log.info(f'Chrome quit {args}'),
        )
    )
    return br


class Bot:
    """The Bot class, see GoogleSearch for demo"""

    def __init__(self,
                 headless=False,
                 proxy=False,
                 window_size=(1920, 5000),
                 screenshot_filename='/tmp/botss-%Y%m%d-%H%M%S.png'):
        """
        :param proxy: True to turn on proxy, see README.md of how to setup proxy and get proxy logs
        """
        self.br = open_chrome(
            headless=headless, proxy=proxy, window_size=window_size)
        self.proxy = self.br.proxy
        self.screenshot_filename = screenshot_filename
        # self.br.play([
        #     ('open', 'https://www.google.co.nz/'),
        # ])
        # print('open', self.br.current_url)
        # self.br.save_screenshot('/tmp/gs.png')

    def save_screenshot(self, screenshot_filename=None):
        """save screenshot to default fname or given fname"""
        if screenshot_filename is None:
            screenshot_filename = self.screenshot_filename
        if screenshot_filename:
            fname = time.strftime(screenshot_filename)
            self.br.save_screenshot(fname)
            log.info(f'screenshot saved to {fname}')

    def sss(self):
        """alias of save_screenshot with default file name"""
        return self.save_screenshot()

    def __getattr__(self, name):
        """redirect any other undefined functions to self.br"""
        if name == 'br':
            raise Exception('call super().__init__() in your __init__')
        return self.br.__getattribute__(name)


class GoogleSearch(Bot):
    """a simple google search for demo"""
    #pylint: disable=missing-docstring

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.play([
            ('open', 'https://www.google.co.nz/'),
        ])
        log.info(f'open {self.current_url}')
        self.save_screenshot()

    def is_recaptcha(self):
        return bool(self.select('form#captcha-form'))

    def search(self, query='something'):
        from bs4 import BeautifulSoup
        self.play([
            ('text', 'form input[name=q]', query, 'clear, enter'),
        ])
        self.save_screenshot()
        htm = self.select('body')[0].html()
        soup = BeautifulSoup(htm, 'html5lib')
        return [
            (g.find('h3').getText().strip(), g.find('a')['href'])
            for g in soup.select('div.srg div.g')
        ]


if __name__ == '__main__':
    # pylint: disable=missing-docstring
    def main():
        br = GoogleSearch(proxy=True)
        print('# all har log with req/resp headers')
        _, har = br.proxy.new_har()  # start new set of har with default options
        print(json.dumps(har, indent=2))
        # or by accessing proxy.har:
        # print(json.dumps(br.proxy.har, indent=2))
        # but proxy.har is a property and triggers requests get everytime
        print(br.search('apple'))
    main()
