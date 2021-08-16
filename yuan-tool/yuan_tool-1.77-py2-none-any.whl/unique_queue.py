import queue
from queue import Full
from time import monotonic as time


class UniqueQueue(queue.Queue):
    def put(self, item, block=True, timeout=None, unique=False):
        """增加了unique参数"""
        with self.not_full:
            # ----- 以下三行为新增代码 -----#
            if unique:
                if item in self.queue:
                    return
            # ----- 新增代码结束 -----#
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()
