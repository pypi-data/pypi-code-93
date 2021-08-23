from test_framework.state import State, DownloadType
from test_framework.upgrade_engine.serial_download import SerialDownloader
from utils.process import MyProcess
from multiprocessing import Queue


class FirmwareDownloader(object):

    def __init__(self, execute_name):
        self.process_run_ = None
        self.results = list()
        self.execute_name = execute_name
        self.runner = None

    def get_download_engine(self, test_parameters):
        if test_parameters["download_type"] == DownloadType.SerialTestPlatform:
            self.runner = SerialDownloader()
        else:
            self.runner = None

    def _run(self, test_parameters, queue):
        try:
            print("FIRMDOWNLOAD", test_parameters)
            self.get_download_engine(test_parameters)
            status, log = self.runner.run(test_parameters)
            ret = State.PASS if status == 0 else State.FAIL
            result = {"name": self.execute_name, "result": ret, "log":log}
            queue.put(result)
        except Exception as e:
            print(e)
            result = None
        return result

    def run(self, test_parameters):
        print(test_parameters)
        queue = Queue()
        self.process_run_ = MyProcess(target=self._run, args=(test_parameters, queue, ))
        self.process_run_.start()
        self.process_run_.join()
        value = queue.get(True)
        self.results.append(value)
        return self.results

    def stop(self):
        print("FirmwareDownloader runner . stop")
        if self.process_run_ is not None:
            ret = self.process_run_.stop()
        else:
            ret = -1
        return ret