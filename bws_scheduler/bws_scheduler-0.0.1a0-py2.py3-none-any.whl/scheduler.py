from __future__ import annotations
from typing import Dict, Tuple, Any, Callable, List, Optional

from bws_scheduler.task import Task
from concurrent.futures import ThreadPoolExecutor
import time
import logging


logger = logging.getLogger(__name__)

       
class Scheduler:
    """Scheduler"""
    def __init__(self, *list_tasks, nthread=4, hearbeat=0.1, wait_max_queue=True, nthread_init=4):
        self.logger = logger
        self.nthread = nthread
        self.nthread_init = nthread_init or nthread
        self._list_tasks = list(list_tasks)
        self.hearbeat = hearbeat
        self.wait_max_queue = wait_max_queue
        self.stop = False
        self.context = {}
        self.state = {}
        self.pool_init = ThreadPoolExecutor(max(self.nthread_init, 1), "init-")
        self.pool = ThreadPoolExecutor(max(self.nthread, 1), "task-")
  
    @property
    def tasks(self):
        return self._list_tasks

    @property
    def num_queue(self):
        return sum([t.is_queue for t in self.tasks])
    
    def add(self, every, name=None, sameness=[], args: Tuple[Any, ...] = (),
            kwargs: Optional[Dict[str, Any]] = {}):
        """
            decorador para agregar tareas
        """
        def wrapper(func: Callable) -> Callable:
            t = Task(name or func.__name__, sameness=sameness)
            t.func(func, *args, **kwargs)
            t.every(every)

            self.add_task(t)
            return func

        return wrapper



    def add_task(self, *tasks):
        for task in tasks:

            if not self.task_exists(task.name):
                # self.logger.info("add_task %s..." % (task.name))
                task.set_context(self, self.context)
                self.pool_init.submit(task.init)
                self._list_tasks.append(task)

    def remove_task(self, task):
        if type(task) is str:
            tasks = [t for t in self.tasks if t.name == task]
            if not tasks:
                return
            task = tasks[0]
        for i, item in enumerate(self._list_tasks):
            if task == item:
                del self._list_tasks[i]
                return 1
        return 0

    def task_exists(self, name):
        return name in [t.name for t in self.tasks]
    
    def get_task_by_name(self, name):
        for t in self.tasks:
            if name == t.name:
                return t
        return None

    def run(self):
        try:
            self.sub()
        except KeyboardInterrupt:
            print("\nexiting...")
            self.join()
            print("bye. thank.")

    def sub(self):
        for task in self.tasks:
            task.set_context(self, self.context)
            self.pool_init.submit(task.init)
            # self.logger.info("%s: %s" % (task.name, task.value_every) )

        while self.stop is False:
            for task in self.tasks:
                if not task.is_available():
                    continue
                
                task.queue()
                # self.logger.info("sub %s..." % (task.model))
                self.pool.submit(task.handle)

                if self.wait_max_queue:
                    is_limit_t = self.num_queue >= self.nthread
                    if is_limit_t:
                        self.logger.debug("is_limit_t => num_queue[%s] >= nthread[%s] last: %s" % (self.num_queue, self.nthread, task.name))

                    while self.num_queue >= self.nthread:
                        time.sleep(self.hearbeat)

            # random.shuffle(self._list_tasks)

            time.sleep(self.hearbeat)

    def join(self):
        self.stop = True;
        self.pool.shutdown()

    
