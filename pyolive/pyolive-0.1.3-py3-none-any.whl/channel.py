import os
import threading
import time
import socket
import json
from queue import Queue
from .adapter import Adapter
from .jobcontext import JobContext


class Channel(threading.Thread):
    def __init__(self, logger):
        super().__init__()
        self.daemon = True
        self.que = Queue()
        self.hostname = socket.gethostname()
        self.logger = logger
        self.runnable = True

    def stop(self):
        self.runnable = False

    def run(self):
        adapter = Adapter(self.logger)
        if not adapter.open():
            self.logger.warning("main, channel: can not open adapter")
            return

        self.logger.debug("main, channel manager start")
        while self.runnable:
            if self.que.qsize() > 0:
                d = self._dequeue()
                adapter.publish(d['exchange'], d['routing_key'], d['body'])
            else:
                time.sleep(5/1000)
        self.logger.debug("main, channel manager stop")
        adapter.close()


    def _dequeue(self):
        return self.que.get()

    def _enqueue(self, exchange, routing_key, json_msg):
        data = {}
        data['exchange'] = exchange
        data['routing_key'] = routing_key
        data['body'] = json_msg
        self.que.put(data)

    def publish_heartbeat(self, namespace, worker_name):
        data = {}
        data['metric-type'] = 2
        data['metric-status'] = 0
        data['metric-zone'] = ''
        data['namespace'] = namespace
        data['process'] = worker_name
        data['psn'] = 0
        data['hostname'] = self.hostname
        routing_key = 'sys.' + namespace + '.heartbeat'
        self._enqueue(Adapter.EXCHANGE_METRIC, routing_key, json.dumps(data))

    def publish_job(self, context:JobContext):
        data = {}
        data['regkey'] = context.regkey
        data['topic'] = context.topic
        data['author'] = context.author
        data['action-id'] = context.action_id
        data['action-ns'] = context.action_ns
        data['action-app'] = context.action_app
        data['action-params'] = context.action_params
        data['job-id'] = context.job_id
        data['timestamp'] = context.timestamp
        data['filenames'] = context.filenames
        data['msgbox'] = context.msgbox

        if context.timestamp == 0:
            routing_key = 'job.des.cwm.early.' + context.topic
        else:
            routing_key = 'job.des.cwm.now.' + context.topic
        json_str = json.dumps(data)
        self.logger.debug("sent message, %s", json_str)
        self._enqueue(Adapter.EXCHANGE_ACTION, routing_key, json_str)

    """status code
    STATUS_STARTED        1  /* 작업시작 */
    STATUS_CREATED        2  /* 작업생성 */
    STATUS_COMPLETED      3  /* 작업정상종료 */
    STATUS_CANCELED       4  /* 작업취소 */
    STATUS_RUNNING        5  /* 작업수행중 */
    STATUS_PENDING        7  /* 일시중지 */
    STATUS_ABORTED        8  /* 작업중단(오류) */
    """
    def publish_notify(self, context:JobContext, text='', status=5, elapsed=0):
        data = {}
        data['job-id'] = context.job_id
        data['job-status'] = status
        data['job-elapsed'] = elapsed
        data['reg-subject'] = context.regkey.split('@')[0]
        data['reg-version'] = context.regkey.split('@')[1]
        data['reg-topic'] = context.topic
        data['action-id'] = context.action_id
        data['action-app'] = context.action_app
        data['action-ns'] = context.action_ns
        data['hostname'] = self.hostname
        data['timestamp'] = int(time.time())
        filesize = 0
        for file in context.filenames:
            try:
                filesize += os.stat(file).st_size
            except:
                continue

        data['filesize'] = filesize
        data['filenames'] = context.filenames
        data['err-code'] = 0
        data['err-mesg'] = text

        routing_key = 'log.' + context.action_ns
        self._enqueue(Adapter.EXCHANGE_LOGS, routing_key, json.dumps(data))

