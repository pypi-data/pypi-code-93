# -*- coding=utf-8 -*-

from threading import Thread
from six.moves import queue as Queue

from .io_helper import IOHelper
from .requests_helper import RequestsHelper

class DownloadHelper(Thread):

    def __init__(self, queue, error_log_file_path, use_proxy=False, socks_proxy=False):
        Thread.__init__(self)
        self.queue = queue
        self.error_log_file_path = error_log_file_path
        self.use_proxy = use_proxy
        self.socks_proxy = socks_proxy

    def run(self):
        while True:
            url, save_path = self.queue.get()
            self.download(url, save_path)
            self.queue.task_done()

    def download(self, url, save_path):
        # print("Downloading %s from %s.\n" % (save_path, url))
        try:
            RequestsHelper.download(url, save_path=save_path, override=True, use_proxy=self.use_proxy, socks_proxy=self.socks_proxy)
        except Exception as err:
            text = '\rurl:\t\t\t\t' + url + '\rsave path:\t' + save_path + '\rerr:\t' + str(err) + '\r'
            IOHelper.save_to_file(self.error_log_file_path, text, mode='a+')