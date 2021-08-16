#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2021/08/09 17:10:05
@Author  :   Wei.fu
@Version :   1.0
@Contact :   wei.fw@bitdeer.com
@Desc    :   None
'''

# here put the import lib
import os
import time
import pickle
import importlib
import threading
from redis import Redis


class WorkTask(object):
    def __init__(self, connect=None, flask_app=None,redis_key_name=''):

        if connect is None:
            self.client = Redis()
        else:
            self.client = connect
        self.key_prefix = 'wq:queue' + redis_key_name
        self.app = flask_app

    def working(self):
        while True:
            try:
                pick_object = self.client.lpop(self.key_prefix)
                if pick_object is not None:
                    data = pickle.loads(pick_object)
                    print(data)
                    pack = data['pack']
                    name = data['name']
                    kwargs = data['kwargs']
                    class_name = data['class_name']
                    class_kwargs = data['class_kwargs']
                    if pack == '__main__':
                        AssertionError('__main__ is not supper')
                    module = importlib.import_module(pack)

                    if self.app:
                        with self.app.app_context():
                            if class_name:
                                module = getattr(module,
                                                 class_name)(**class_kwargs)
                                run_fun = getattr(module, name)
                            else:
                                run_fun = getattr(module, name)
                            run_fun(**kwargs)
                    else:
                        if class_name:
                            module = getattr(module,
                                             class_name)(**class_kwargs)
                            run_fun = getattr(module, name)
                        else:
                            run_fun = getattr(module, name)
                        run_fun(**kwargs)

                else:

                    time.sleep(2)
            except Exception as e:
                print('error', e)
                time.sleep(1)

    def thread(self):
        thread = threading.Thread(target=self.working)
        thread.start()

    def start(self):
        self.working()


if __name__ == '__main__':
    WorkTask().working()
