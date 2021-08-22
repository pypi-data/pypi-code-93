import os
import sys
import signal
import socket
import json
from .adapter import Adapter
from .channel import Channel
from .worker import Worker
from .heartbeat import Heartbeat
from .log import create_logger, get_log_path
from .jobcontext import JobContext


class Olive:
    def __init__(self, namespace):
        self.worker_name = 'ovd-worker'
        self.namespace = namespace
        self.adapter = None
        self.channel = None
        self.tasks = []
        self.logger = create_logger(self.namespace)
        self.logger.info("------------------------------------------------")
        self.logger.info("main, run %s", self.namespace)
        print("main, run", self.namespace)

    def _get_pid_filename(self):
        file = self.worker_name + '@' + socket.gethostname() + '.pid'
        path = get_log_path()
        return os.path.join(path, file)

    def _create_pid_file(self):
        name = self._get_pid_filename()
        pid = os.getpid()
        with open(name, "w") as f:
            f.write(str(pid))

    def _remove_pid_file(self):
        name = self._get_pid_filename()
        if os.path.exists(name):
            os.remove(name)

    def _callback_signal(self, signum, frame):
        self.channel.stop()
        self.adapter.stop_consume()

    def _callback_subscribe(self, ch, method, properties, body):
        json_str = body.decode()
        self.logger.debug("received message, %s", json_str)
        message = json.loads(json_str)
        app_name = message['action-app']
        app_params = {}
        _s1 = message['action-params']
        _s2 = _s1.split('&')
        for i in range(len(_s2)):
            _s3 = _s2[i].split('=')
            app_params[_s3[0]] = _s3[1]

        # worker를 thread로 실행함
        for task in self.tasks:
            if app_name == task['app']:
                self.logger.info("main, start app, %s", app_name)
                ctx = JobContext(message)
                w = Worker(task['resource'], self.channel, self.logger, ctx)
                w.start()
                self.logger.info("main, stop app, %s", app_name)

    def run(self):
        self.adapter = Adapter(self.logger)
        if not self.adapter.open():
            return

        self._create_pid_file()
        # channel manager start
        self.channel = Channel(self.logger)
        self.channel.start()

        # heartbeat timer start
        heartbeat = Heartbeat(self.channel, self.namespace, self.worker_name)
        heartbeat.start()

        # signal 처리
        signal.signal(signal.SIGTERM, self._callback_signal)
        signal.signal(signal.SIGINT, self._callback_signal)

        # consume manager looping
        self.adapter.start_consume(self.namespace, self._callback_subscribe)

        # end job
        self.logger.info("main, exit")
        print("main, exit")
        self.adapter.close()
        heartbeat.stop()
        self._remove_pid_file()
        sys.exit(0)

    def add_resource(self, resource, app_name):
        task = {}
        task['app'] = app_name
        task['resource'] = resource
        self.tasks.append(task)
