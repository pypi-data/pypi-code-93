from __future__ import absolute_import
from __future__ import unicode_literals

from tqdm import tqdm


class Processor:
    def __init__(self):
        self.func_queue = {}
        self.nocols = 80
        self.ascii = ' ='
        self.bar_format = '{l_bar}{bar}|'

    def run_with_bar(self, queue_name):
        progress_bar = tqdm(iterable=self.func_queue[queue_name], ncols=self.nocols, ascii=self.ascii, bar_format=self.bar_format)
        for func in progress_bar:
            progress_bar.set_description("\t队列: {} --> 正在执行方法: {}".format(queue_name, func.__name__))
            func(self)

    def append_queue(self, queue_name, fn_name):
        try:
            self.func_queue[queue_name].append(fn_name)
        except KeyError:
            self.func_queue[queue_name] = []
            self.func_queue[queue_name].append(fn_name)

    @staticmethod
    def in_queue(queue_name):
        def get_fn(func):
            def wrap(self):
                self.append_queue(queue_name, func)
            return wrap
        return get_fn
