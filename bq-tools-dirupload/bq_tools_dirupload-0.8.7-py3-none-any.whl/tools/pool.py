from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import range
from builtins import object
import os
import sys
import subprocess
from threading import Thread, Lock
import logging
from time import sleep
from queue import Queue, Empty

def worker(queue, thread_tasks, worker_id):
    """Worker waits forever command requests and executes one command at a time

    @param queue: is a queue of command requests
    @param thread_tasks: mapping worker_id -> (task, subprocess) (or None)
    @param worker_id: integer identifying this worker

    requests  = {
      workfun :  callable
      args         : A list of arguments
      kw_args      : dict of args
      on_success   : callback with (request) when success,
      on_fail      : callback with (request) when fail,
    }

    This routine will add the following fields:
    {
       return_code : return code of the command
       with_exception : an exception when exited with excepttion
    }
    """
    for request in iter(queue.get, None):
        if request is None:
            return

        callme = request['on_fail']
        workfun = request['workfun']
        is_success = request.get ('is_success')
        args = request.get('args') or []
        kw_args = request.get('kw_args') or {}
        try:
            # remember which request this thread is working on
            thread_tasks[worker_id] = (request, workfun)
            # wait for termination

            retvalue = workfun(*args, **kw_args)
            request ['return_value']=retvalue
            if  callable(is_success) and is_success(retvalue) :
                callme = request['on_success']

        except Exception as e:
            request['with_exception'] = e
            exc_type, exc_val, exc_tb = request['exc_info'] = sys.exc_info()
            request['with_exc_type'] = exc_type
            request['with_exc_val'] = exc_val
            request['with_exc_tb'] =   exc_tb
        finally:
            thread_tasks[worker_id] = None
            if callable(callme):
                callme(request)


class ProcessManager(object):
    "Manage a set of threads to execute limited subprocess"
    def __init__(self, limit=4, workfun=None, args=None, kw_args=None, is_success=lambda x:x , on_success=None, on_fail=None ):
        self.pool = Queue()
        self.pool_lock = Lock()
        self.thread_tasks = [None for _ in range(limit)]
        self.default_request = dict (workfun=workfun, args=args, kw_args=kw_args, is_success=is_success, on_success=on_success, on_fail=on_fail)
        self.threads = [Thread(target=worker, args=(self.pool, self.thread_tasks, tid)) for tid in range(limit)]
        for t in self.threads: # start workers
            t.daemon = True
            t.start()
        self.logger = logging.getLogger ('pool')

    def isbusy (self):
        return not self.pool.empty()

    def schedule  (self,  **kw):
        """Schedule  a process to be run when a worker thread is available

        @param process: a request see "worker"
        @param success:  a callable to call on success
        @param fail:  a callable to call on failure
        """
        process = self.default_request.copy()
        process.update (kw)
        self.pool.put_nowait (process)

    def stop (self):
        for _ in self.threads: self.pool.put(None) # signal no more commands
        for t in self.threads:
            t.join()    # wait for completion

    def kill(self, selector_fct = None):
        """Remove queue entries and kill workers for specific task

        @param selector_fct: fct to identify processes to kill fct(process)->boolean
        """
        # first, remove any queue entries for task
        qsize = self.pool.qsize()
        try:
            for _ in range(qsize):   # upper bound on number of iterations necessary (queue can only shrink while we iterate)
                task = self.pool.get_nowait()
                if task is None or not (selector_fct is None or selector_fct(task)):
                    # not to be deleted => put it back into queue
                    self.pool.put_nowait(task)
                else:
                    self.logger.debug("task removed from queue: %s" % task)
        except Empty:
            pass
        # kill all threads associated with task
        for tid in range(len(self.thread_tasks)):
            if self.thread_tasks[tid] is None:
                continue
            task, subproc = self.thread_tasks[tid]
            if selector_fct is None or selector_fct(task):
                # found matching task => interrupt associated thread
                self.logger.debug("interrupting function %s" % subproc)
                #subproc.terminate()
                # wait for thread to terminate
                # (following will not always work: thread may pick another task while we wait...)
                #while self.thread_tasks[tid] is not None:
                #    sleep(0.2)
                #self.logger.debug("task interrupted")
