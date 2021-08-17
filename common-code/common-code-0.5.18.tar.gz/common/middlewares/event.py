import json
from queue import Queue
from threading import Thread
from django.utils.deprecation import MiddlewareMixin
from middleware.estools import ESClient

from common.middlewares import logger


class EventMiddleware(MiddlewareMixin):

    def start(self, host, port, username=None, password=None, index='event'):
        self.q = Queue()
        self.index = index
        self.es_client = ESClient()
        self.es = self.es_client.conn(host=host, port=port, username=username, password=password)
        Thread(target=self.send_event).start()

    def process_response(self, request, response):
        try:
            if response.status_code < 300 and request.method != 'GET':
                data = self.parsing(request, response)
                if data:
                    self.q.put(data)
        except Exception as e:
            logger.exception(e)
        return response

    def parsing(self, request, response):
        data = json.loads(request.body)
        return data

    def send_event(self):
        while True:
            try:
                body = self.q.get()
                self.es_client.index(index=self.index, body=body)

            except Exception as e:
                logger.exception(e)
