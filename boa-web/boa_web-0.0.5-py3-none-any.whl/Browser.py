import os, sys, threading
from cefpython3 import cefpython as cef
from flask import Flask, jsonify, json, request, render_template
try:
    from ._utils import *
except ImportError:
    from _utils import *

# globals (for DEFAULT arguments to BoaCage)
BOA_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_PORT = 5000
DEFAULT_ICON = os.path.join(BOA_DIR, "icons/logo.png")
DEFAULT_TITLE = "A boa_web application"
HTMLBoilerPlate = '''<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        {{ css_sources }}
        <title>{{ title }}</title>
    </head>
    <body>
        <header>
            {{ header }}
        </header>
        {{ body }}
        <footer>
            {{ footer }}
        </footer>
        {{ script_sources }}
    </body>
</html>'''


class Page:
    def __init__(self, root, **args):
        import os
        from jinja2 import Template
        self.template = Template(HTMLBoilerPlate)
        self.html = self.template
        self.args = args
        self.root = root
        os.makedirs("templates", exist_ok=True)

    def build(self):
        body = str(self.root)
        self.html = self.template.render(body=body, **self.args)
        # print(body)
        return self.html

    def attach(self, cage):
        import os, colors 
        self.root.encage(cage)
        for binding in self.root._get_bindings():
            # print("—"*os.get_terminal_size().columns)
            # print(binding)
            cage._bind(binding["name"], binding["callback"])
            cage.execJS(binding["jscode"])
        print(colors.color("attached all callbacks", fg="green", style="bold"))

    def save(self, path):
        open(path, "w").write(self.html)

class LoadHandler:
    def __init__(self, cage, scale=1, rotation=0):
        self.cage = cage
        self.scale = scale
        self.rotation = rotation

    def OnLoadingStateChange(self, browser, is_loading, **kwargs):
        import threading, colors
        self.browser = browser
        if not is_loading:
            print(colors.color("loading completed", fg="green", style="bold"))
            # print(browser.GetUrl())
            while True:
                try:
                    # self.browser.ExecuteJavascript('console.log("hello world");')
                    scale = self.scale*100
                    self.browser.ExecuteJavascript(f"console.log('scale set to {self.scale} ');")
                    self.browser.ExecuteJavascript(f"document.body.style.zoom = '{scale}%'")
                    self.browser.ExecuteJavascript(f"console.log('{self.rotation} deg rotation applied');")
                    self.browser.ExecuteJavascript(f'''document.body.style.setProperty("-webkit-transform", "rotate({self.rotation}deg)", null);''')
                    break
                except: pass
            self.cage.dom_loaded = True
    # def OnLoadStart(self, browser, **_):
    #     '''Can update url bar if it exists'''
    #     if self.browser:
    #         self.browser_frame.master.navigation_bar.set_url(browser.GetUrl())
# class ExecJSHandler:
#     def __init__(self, jscode):
#         self.jscode = jscode

#     def OnLoadingStateChange(self, browser, is_loading, **_):
#         if not is_loading:
#             browser.ExecuteJavascript(self.jscode)
class BoaCage:
    '''
    The class for the browser object
    '''
    def __init__(self, name, **kwargs):
        check_versions(cef)
        self.cef = cef
        sys.excepthook = self.cef.ExceptHook
        directory = os.path.realpath(name)
        print(name, directory)
        # init_dirs(directory) # create the templates and static directory at the correct spot.
        self.app = Flask(name)
        self.scale = kwargs.get("scale", 1)
        self.rotation = kwargs.get("rotation", 0)
        self.icon = kwargs.get("icon", DEFAULT_ICON)
        self.port = kwargs.get("port", DEFAULT_PORT)
        self.title = kwargs.get("title", DEFAULT_TITLE)
        self.dom_loaded = False
        print(self.cef.WindowInfo())

    def _start(self):
        self.cef.Initialize()
        self.browser = self.cef.CreateBrowserSync(url="https://www.google.com/", window_title=self.title)
        # self.browser.SetClientHandler(LifespanHandler(self))
        self.browser.SetClientHandler(LoadHandler(self, scale=self.scale, rotation=self.rotation))
        # self.browser.SetClientHandler(FocusHandler(self))
        # print(dir(self.cef.WindowInfo()))
        self.jsBindings = cef.JavascriptBindings(bindToFrames=False, bindToPopups=False)
        self.cef.MessageLoop()
        self.cef.Shutdown()

    def _update_bindings(self):
        '''Might not be the most efficient code.'''
        self.browser.SetJavascriptBindings(self.jsBindings)

    def _bind(self, name, callback):
        '''Bind a Javascript function to the browser.'''
        self.jsBindings.SetFunction(name, callback)
        self._update_bindings()

    def _run(self):
        self.app.run(port=self.port)

    def _close(self):
        self.force_close
        self.browser.CloseBrowser(force_close=True)

    def _wait_for_browser(self, verbose=False):
        import colors
        while True:
            try: 
                self.browser
                if verbose: print(colors.color("waiting for browser init", fg="yellow", style="bold")); break
            except: pass

    def setZoomFactor(self, scale=1):
        '''
        Set the zoom in the browser window.
        '''
        self.scale = scale
        percent_scale = self.scale*100
        self.browser.ExecuteJavascript(f"document.body.style.zoom = '{percent_scale}%'")

    def rotate(self, rotation):
        self.rotation = rotation
        self.browser.ExecuteJavascript(f'''document.body.style.setProperty("-webkit-transform", "rotate({self.rotation}deg)", null);''')

    def execJS(self, jscode):
        '''
        Execute javascript. The while loop is a temporary way to deal with dealy in browser creation. (self.browser won't exist till CreateBrowserSync finishes excution)
        '''
        while True:
            if self.dom_loaded: break
        # print("dom_loaded=", self.dom_loaded)
        self.browser.ExecuteJavascript(jscode)

    def setTitle(self, title):
        '''need tp use SetTitle for windows.'''
        import platform
        self.browser.SetTitle(title)

    def setIcon(self, icon=None):
        if icon is None: icon = self.icon
        windowId = self.browser.GetWindowHandle()
        print(windowId)

    def getZoomFactor(self):
        return self.scale

    def alert(self, message):
        self.browser.ExecuteJavascript(f"alert('{message}');")

    def setUrl(self, url=None):
        if url is None: url = f"http://127.0.0.1:{self.port}/"
        while True:
            try:
                self.browser.LoadUrl(url)
                break
            except: pass
        # request = self.cef.Request.CreateRequest()
        # request.SetUrl(url)
    # def endpoints(self):
    #     @self.app.route("/", methods=["GET","POST"])
    #     def _render_index(self):
    #         return render_template("index.html")
    def run(self):
        import time
        @self.app.route("/", methods=["GET","POST"])
        def _render_index():
            return render_template("index.html")
        self.browserThread = threading.Thread(target=self._start)
        self.browserThread.start()
        self.appThread = threading.Thread(target=self._run)
        self.appThread.start()
        self.setUrl(f"http://127.0.0.1:{self.port}/")

class TestBrowser:
    def __init__(self, browser, interval=1):
        self.browser = browser
        self.interval = interval

    def test_zoom(self, sizes=[1.25, 0.8, 2]):
        import time
        for scale in sizes:
            time.sleep(self.interval)
            print(f"zooming to {100*scale}%")
            self.browser.setZoomFactor(scale=scale)

    def test_alert(self, msg="Hello World!"):
        import time
        time.sleep(self.interval)
        print("alerting:")
        self.browser.alert(msg)


if __name__ == '__main__':
    import time
    import colors
    browser = BoaCage(port=5000)
    browser.run()
    print(colors.color("app launched succesfully", fg="green", style="bold"))
    print(colors.color("running tests!", fg="yellow", style="bold"))
    tester = TestBrowser(browser=browser, interval=1)
    tester.test_zoom(sizes=[1.25,0.8,2])
    tester.test_alert(msg="Hello World")
    # browser.setIcon()

# class WidgetNode:
#     def __init__(self, widget, parent=None):
#         '''
#         widget: Instance of boa_web.Widgets.Widget
#         parent: Instance of boa_web.Browser.WidgetNode
#         '''
#         self.parent = parent
#         self.widget = widget
#         if parent: self.parent.add_child(self)
#         self.children = []

#     def add_child(self, child):
#         self.children.append(child)

#     def _compile(self):
#         '''
#         Join all children, by placing each of them on a new line
#         '''
#         body = "\n".join([child_widget._compile() for child_widget in self.children])
#         self.widget.setHtml(body)

#         return str(self.widget)
# class PlacementManager:
#     '''A class that manages the relative layout of all widgets in the dom tree. It is also responsible for auto-generating the html document from the DOM tree during run time.'''
#     def __init__(self):
#         self._root_node = None
#         self._compiled_html = None
#         self._widget_nodes = {}

#     def _pack(self, widget, parent):
#         '''
#         Assuming instances of boa_web.Widgets.Widget passed for the immediate parent widget and the widget
#         '''
#         if self._root_node:
#             parent_node = self._widget_nodes[parent.id]
#             self._widget_nodes[widget.id] = WidgetNode(widget, parent_node) 
#         else:
#             self._root_node = WidgetNode(widget)
#             self._widget_nodes[widget.id] = self._root_node

#     def _grid(self):
#         pass

#     def compile(self):
#         self._compiled_html = self._root_node._compile()

#     def save(self, path):
#         self.compile()
#         open(path, "w").write(self._compiled_html)

# Hello world example. Doesn't depend on any third party GUI framework.
# Tested with CEF Python v57.0+.
#
# ==== High DPI support on Windows ====
# To enable DPI awareness on Windows you have to either embed DPI aware manifest
# in your executable created with pyinstaller or change python.exe properties manually:
# Compatibility > High DPI scaling override > Application.
# Setting DPI awareness programmatically via a call to cef.DpiAware.EnableHighDpiSupport
# is problematic in Python, may not work and can cause display glitches.