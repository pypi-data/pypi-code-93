import sys
import threading, time, signal, logging
from datetime import timedelta

class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass

def service_shutdown(signum, frame):
    raise ServiceExit

class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
                self.stopped.set()
                self.join()
    def run(self):
            while not self.stopped.wait(self.interval.total_seconds()):
                res=self.execute(*self.args, **self.kwargs)
                if res is False:
                    self.stop()

class Timeloop():
    def __init__(self):
        self.jobs = []
        logger = logging.getLogger('timeloop')
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.setLevel(logging.INFO)
        self.logger = logger

    def _add_job(self, func, interval, *args, **kwargs):
        j = Job(interval, func, *args, **kwargs)
        self.jobs.append(j)

    def _block_main_thread(self):
        signal.signal(signal.SIGTERM, service_shutdown)
        signal.signal(signal.SIGINT, service_shutdown)

        while True:
            try:
                time.sleep(1)
            except ServiceExit:
                self.stop()
                break

    def _start_jobs(self, block):
        for j in self.jobs:
            j.daemon = not block
            j.start()
            self.logger.info("Registered job {}".format(j.execute))

    def _stop_jobs(self):
        for j in self.jobs:
            self.logger.info("Stopping job {}".format(j.execute))
            j.stop()

    def job(self, seconds):
        def decorator(f):
            self._add_job(f, timedelta(seconds=seconds))
            return f
        return decorator

    def stop(self):
        self._stop_jobs()
        self.logger.info("Timeloop exited.")

    def start(self, block=False):
        self.logger.info("Starting Timeloop..")
        self._start_jobs(block=block)

        self.logger.info("Timeloop now started. Jobs will run based on the interval set")
        if block:
            self._block_main_thread()

if __name__ == "__main__":
    tl = Timeloop()
    @tl.job(seconds=2)
    def sample_job_every_2s():
        print("2s job current time : {}".format(time.ctime()))
    tl.start(block=True)
