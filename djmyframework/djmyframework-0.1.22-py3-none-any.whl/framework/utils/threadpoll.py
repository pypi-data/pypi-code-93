# -*- coding:UTF-8 -*-
# 线程池 by xzr

import functools
import threading
import time
import traceback
import queue



def async_func(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        my_thread.setDaemon(True)
        my_thread.start()

    return wrapper


class ThreadWork(threading.Thread):
    def __init__(self, manager, mark):
        super(ThreadWork, self).__init__()
        self.manager = manager
        self.setDaemon(True)
        self.mark = mark

    def run(self):
        while 1:
            try:
                func_grgs = self.manager.jobQ.get()
                if func_grgs:
                    # print '%s get the job' % self.mark
                    res = func_grgs[0](*func_grgs[1])
                    if not self.manager.not_ret:
                        self.manager.resultQ.put(res)
                    self.manager.jobQ.task_done()
                else:
                    self.manager.is_close_threads.remove(self.mark)
                    self.manager.jobQ.task_done()
                    break

            except:
                traceback.print_exc()
                time.sleep(0.01)


class ThreadPool(object):
    def __init__(self, pool_size=100, not_ret=False):
        self.pool_size = pool_size
        self.not_ret = not_ret
        self.jobQ = queue.Queue(0)
        self.resultQ = queue.Queue(0)
        self.threads = []
        self.is_close_threads = []

        for i in range(pool_size):
            t = ThreadWork(self, i)
            self.is_close_threads.append(i)
            t.start()
            self.threads.append(t)
        self.job_num = 0

    def append(self, func, args=()):

        self.jobQ.put((func, args))
        self.job_num += 1

    def get_result(self):
        result_num = 0
        while 1:
            try:
                yield self.resultQ.get_nowait()
                result_num += 1
                if self.job_num == result_num or not self.is_close_threads: break
            except queue.Empty:
                time.sleep(0.01)

    def get_all_result(self):
        return [r for r in self.get_result()]

    def close(self):
        for _ in range(len(self.threads)):
            self.jobQ.put(None)
        self.join()

    def join(self):
        for t in self.threads:
            t.join()

    def __del__(self):
        self.close()
        self.join()


if __name__ == '__main__':
    def test(x):
        time.sleep(10)
        return x


    tp = ThreadPool(10)
    for x in range(10):
        tp.append(test, (x,))

    print(tp.get_all_result())
    # for x in tp.get_result():
    #    print x
    tp.close()

