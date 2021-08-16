import psutil
from multiprocessing import Process, Queue, Value, Array

from zwutils.dlso import upsert_config
from zwutils.logger import cologger

class ZWTask(Process):
    def __init__(self, target=None, name=None, args=None, daemon=True, 
                queue=None, array=None, value=None, cfg=None, **kwargs):
        super().__init__(name=name, daemon=daemon)
        cfgdef = {}
        self.cfg = upsert_config(None, cfgdef, cfg, kwargs)

        self.target = target
        self.name = name
        self.args = list(args or ())
        self.queue = queue
        self.array = array
        self.value = value

    def run(self):
        cfg = self.cfg
        log = self.logger()
        if self.target is None:
            exit(1)
        log.info('Process #%s start.', self.pid)
        self.target(self, *self.args)
        log.info('Process #%s return.', self.pid)
        exit(0)
    
    def kill(self):
        if self.is_alive() and psutil.pid_exists(self.pid):
            p = psutil.Process(self.pid)
            p.kill()
    
    def status(self):
        _psobj = psutil.Process(self.pid)
        if self.is_finish():
            return psutil.STATUS_STOPPED
        elif not psutil.pid_exists(self.pid):
            return psutil.STATUS_STOPPED
        return _psobj.status()
    
    def is_finish(self):
        return self.exitcode == 0
    
    def logger(self):
        self.log = cologger(__name__, self.name or self.pid)
        return self.log
    
    @classmethod
    def run_tasks(cls, target, args, queue=None, array=None, value=None, name_prefix=None, targetclass=None):
        name = name_prefix or 'Task'
        tcls = targetclass or ZWTask
        q = queue or Queue()
        a = array or Array('i', [0]*len(args))
        v = value or Value('i', 0)
        tasks = [tcls(target=target, name='%s-%d'%(name, i), args=o, queue=q, array=a, value=v) \
            for i, o in enumerate(args)]
        for t in tasks:
            t.start()
        return tasks, q, a, v
