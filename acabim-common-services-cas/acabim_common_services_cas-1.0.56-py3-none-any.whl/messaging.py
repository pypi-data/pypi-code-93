import json
import logging
import os
import socket
import uuid
from json import JSONDecodeError
from multiprocessing import current_process
from threading import Thread, get_ident

import pika
import sys
from pika.exceptions import ChannelWrongStateError, ConnectionWrongStateError

from cas import utils

_LOGGER = logging.getLogger('cas.acabim.messaging')

EXPECTED_MSG_TYPE = {}  # fill in with the expected msg types that needs to be sent to MassTransit


class MessagingHandler:
    def __init__(self, connection_name='cas.messaging.PythonClient'):
        self.current_status = {}
        self.connection_name = connection_name
        self.__pending_listeners = {}
        self.__connected_callbacks = []
        self.__disconnected_callbacks = []
        self.__create_connection()
        self.__create_thread()

    def __del__(self):
        if self.is_connected():
            self.stop()

    def __create_connection(self):
        if not hasattr(self, '__connection'):
            user_name = os.getenv('ACABIM_MESSAGING_USERNAME', 'guest')
            password = os.getenv('ACABIM_MESSAGING_PASSWORD', 'guest')
            host = os.getenv('ACABIM_MESSAGING_HOST', 'localhost')
            credentials = pika.PlainCredentials(user_name, password)
            params = pika.ConnectionParameters(host=host, credentials=credentials, retry_delay=10,
                                               connection_attempts=10,
                                               client_properties={
                                                   'connection_name': self.connection_name,
                                                   'hostname': socket.gethostname(),
                                                   'python_version': sys.version,
                                                   'process_id': os.getpid()
                                               })
            self.__connection = pika.SelectConnection(params, on_open_callback=self.__on_connected,
                                                      on_close_callback=self.__on_closed)

    def __create_thread(self):
        if not hasattr(self, '_MessagingHandler__bk_thread'):
            self.__bk_thread = Thread(target=self.__connect, name='cas.messaging.ConnectionHandler')
            self.__bk_thread.daemon = False

    def is_connected(self):
        try:
            return self.__connection.is_open and self.__channel.is_open
        except AttributeError:
            return False

    def start(self):
        if not self.is_connected():
            self.__create_connection()
            self.__create_thread()
            self.__bk_thread.start()

    def stop(self):
        self.__remove_connection()

    def listen(self, queue_name, callback):
        if callback is None:
            raise TypeError('callback cannot be none')

        self.__pending_listeners[queue_name] = callback
        self.__channel.exchange_declare(queue_name, exchange_type='fanout', durable=True,
                                        callback=lambda ex: self.__on_exchange_declared(ex, queue_name))

    def wait_for_connection(self):
        _LOGGER.debug('Waiting for connection')
        while True:
            if self.is_connected():
                _LOGGER.debug('Connection established')
                break

    def respond(self, req_queue_name, res_message_body, req_message):
        """ Respond with a message for a received request """
        if not MessagingHandler.can_respond(req_message):
            _LOGGER.critical('Cannot respond to msg %s, No-Respond-Address-Found', json.dumps(req_message))
        else:
            res_queue = MessagingHandler.__get_response_queue_name(req_message)
            body = MessagingHandler.__create_response_message(req_queue_name, res_message_body, req_message)
            try:
                self.__channel.basic_publish(exchange=res_queue, routing_key='', body=body,
                                             properties=MessagingHandler.__get_header_properties())
                _LOGGER.debug(f'Message published on queue {res_queue}: Type: RespondSendMessage')
            except ChannelWrongStateError as channel_error:
                _LOGGER.exception(channel_error, 'Unable to send message - Channel not open')
            except AttributeError:
                _LOGGER.error('No connection found to respond with the message')

    def send_message(self, queue, res_message_body, req_message):
        try:
            body = MessagingHandler.__create_response_message(queue, res_message_body, req_message)
            try:
                self.__channel.basic_publish(exchange=queue, routing_key='', body=body,
                                             properties=MessagingHandler.__get_header_properties())
                _LOGGER.debug(f'Message published on queue {queue}: Type: BasicSendMessage')
            except ChannelWrongStateError as exc:
                _LOGGER.exception(exc, 'Unable to send message - Channel not open')
        except AttributeError as ex:
            _LOGGER.exception(ex)

    def send_fault_message(self, queue, exception, stack_trace, response, req_message):
        try:
            body = MessagingHandler.__create_fault_message(queue, str(exception), stack_trace, response, req_message)
            res_queue = MessagingHandler.__get_fault_queue_name(queue)
            try:
                self.__channel.basic_publish(exchange=res_queue, routing_key='', body=body,
                                             properties=MessagingHandler.__get_header_properties())
                _LOGGER.debug(f'Message published on queue {res_queue}: Type: FaultSendMessage')
            except ChannelWrongStateError as channel_error:
                _LOGGER.exception(channel_error, 'Unable to send message - Channel not open')
        except AttributeError as a_error:
            _LOGGER.exception(a_error, 'No connection found')

    def add_connected_callback(self, callback):
        self.__connected_callbacks.append(callback)

    def add_disconnected_callback(self, callback):
        self.__disconnected_callbacks.append(callback)

    def __connect(self):
        _LOGGER.info('Starting connection')
        try:
            self.__connection.ioloop.start()
        except KeyboardInterrupt:
            self.__connection.close()

    def __remove_connection(self):
        """ Removes the connection and the channel after closing it """
        try:
            _LOGGER.debug('Channel going down')
            self.__channel.close()
            del self.__channel
        except AttributeError:
            _LOGGER.warning('Unable to close channel - Channel not found')
        except ChannelWrongStateError:
            _LOGGER.warning('Unable to close channel - Channel may have already been closed')
            del self.__channel

        try:
            _LOGGER.debug('Connection going down')
            self.__connection.ioloop.add_callback_threadsafe(self.__connection.ioloop.stop)
            self.__connection.close()
            del self.__connection
        except AttributeError:
            _LOGGER.warning('Unable to remove connection - Connection not found')
        except ConnectionWrongStateError:
            _LOGGER.warning('Unable to close connection - connection may have already been closed')
            del self.__connection

        try:
            _LOGGER.info('Waiting for the background thread to exit')
            if get_ident() != self.__bk_thread.ident:
                self.__bk_thread.join()
            del self.__bk_thread
            _LOGGER.info('Background thread removed')
        except AttributeError:
            pass

    def __on_connected(self, opened_connection):
        _LOGGER.info('Connection Opened with Host: %s', opened_connection.params.host)
        self.__connection.channel(on_open_callback=self.__on_channel_open)

    def __on_closed(self, closed_connection, exception):
        _LOGGER.exception(exception)
        _LOGGER.critical('Connection closed with Host: %s', closed_connection.params.host)
        self.__remove_connection()
        for callback in self.__disconnected_callbacks:
            callback(self)
        self.__disconnected_callbacks.clear()

    def __on_channel_open(self, opened_channel):
        _LOGGER.info('Channel open with Host: %s, Number: %s', opened_channel.connection.params.host,
                     opened_channel.channel_number)
        self.__channel = opened_channel
        for call in self.__connected_callbacks:
            call(self)
        self.__connected_callbacks.clear()

    def __on_exchange_declared(self, exchange, exchange_name):
        _LOGGER.debug('Exchange Declared - Message: %s, ExchangeName: %s', exchange.method.NAME, exchange_name)
        if exchange.method.NAME == 'Exchange.DeclareOk':
            _LOGGER.debug('Declaring Queue: %s', exchange_name)
            self.__channel.queue_declare(queue=exchange_name, durable=True,
                                         callback=lambda result: self.__on_queue_declared(result, exchange_name))
        else:
            _LOGGER.critical('Invalid exchange message - Unable to declare queue %s', exchange_name)
            raise Exception('Invalid Response when declaring exchange \'{0}\', Received: {1} '
                            .format(exchange_name, exchange.method.NAME))

    def __on_queue_declared(self, queue, queue_name):
        _LOGGER.debug('Queue Declared - Message: %s, QueueName: %s', queue.method.NAME, queue_name)
        if queue.method.NAME == 'Queue.DeclareOk':
            _LOGGER.debug('Binding Queue %s to exchange %s', queue_name, queue_name)
            self.__channel.queue_bind(exchange=queue_name, queue=queue_name, routing_key='',
                                      callback=lambda result: self.__on_queue_ready(result, queue_name))
        else:
            _LOGGER.critical('Invalid exchange message - Unable to bind queue %s', queue_name)
            raise Exception('Invalid Response when binding queue \'{0}\', Received: {1}'
                            .format(queue_name, queue.method.NAME))

    def __on_queue_ready(self, queue, queue_name):
        if queue.method.NAME == 'Queue.BindOk':
            _LOGGER.info('Queue Ready: %s', queue_name)
            if queue_name in self.__pending_listeners:  # if we have a pending listener that means we have to listen
                _LOGGER.info('Listener found for Queue: %s', queue_name)
                self.__channel.basic_consume(queue=queue_name, auto_ack=True,
                                             on_message_callback=lambda channel, method, properties, body:
                                             self.__on_new_message_received(queue_name, body))

    def __on_new_message_received(self, queue_name, body):
        content = MessagingHandler.__verify_and_get_message_content(body)
        if queue_name in self.__pending_listeners:
            self.__pending_listeners[queue_name](content)

    @staticmethod
    def can_respond(message):
        return 'responseAddress' in message

    @staticmethod
    def __verify_and_get_message_content(body):
        try:
            return json.loads(body)
        except JSONDecodeError:
            _LOGGER.critical('Unhandled Body content: Invalid Message - Unable to parse JSON')
            _LOGGER.critical('Body: "%s"', body.decode('utf8'))
            _LOGGER.exception(JSONDecodeError)

    @staticmethod
    def __get_response_queue_name(req_message_content):
        return req_message_content['responseAddress'].split('/').pop().split('?')[0]

    @staticmethod
    def __get_fault_queue_name(expected_msg_type):
        return 'MassTransit:Fault--{0}--'.format(expected_msg_type)

    @staticmethod
    def __create_response_message(queue, response_message_content, req_message):
        res_message = {'messageId': str(uuid.uuid4())}
        if req_message is not None and 'requestId' in req_message:
            res_message['requestId'] = req_message['requestId']

        if req_message is not None and 'conversationId' in req_message:
            res_message['conversationId'] = req_message['conversationId']
        else:
            res_message['conversationId'] = str(uuid.uuid4())

        if req_message is not None and 'initiatorId' in req_message:
            res_message['initiatorId'] = req_message['initiatorId']
        else:
            res_message['initiatorId'] = str(uuid.uuid4())

        if queue in EXPECTED_MSG_TYPE:
            res_message['messageType'] = ['urn:message:{0}'.format(EXPECTED_MSG_TYPE[queue])]
        else:
            res_message['messageType'] = ['urn:message:{0}'.format(queue)]
            _LOGGER.warning('No message_type found, Using the queue name')

        res_message['message'] = response_message_content
        res_message['sentTime'] = utils.current_time_str()
        res_message['headers'] = {}
        res_message['host'] = MessagingHandler.__get_host_info()
        return bytes(json.dumps(res_message), 'utf8')

    @staticmethod
    def __create_fault_message(queue, exception_msg, stack_trace, response, req_message):
        res_message = {'messageId': str(uuid.uuid4())}
        if req_message is not None and 'requestId' in req_message:
            res_message['requestId'] = req_message['requestId']

        if req_message is not None and 'conversationId' in req_message:
            res_message['conversationId'] = req_message['conversationId']
        else:
            res_message['conversationId'] = str(uuid.uuid4())

        if req_message is not None and 'initiatorId' in req_message:
            res_message['initiatorId'] = req_message['initiatorId']
        else:
            res_message['initiatorId'] = str(uuid.uuid4())

        if queue in EXPECTED_MSG_TYPE:
            res_message['messageType'] = ['urn:message:MassTransit:Fault[[{0}]]'.format(EXPECTED_MSG_TYPE[queue]),
                                          'urn:message:MassTransit:Fault']
        else:
            res_message['messageType'] = ['urn:message:MassTransit:Fault[[{0}]]'.format(queue),
                                          'urn:message:MassTransit:Fault']
            _LOGGER.warning('No message_type found, Using the queue name')

        fault_message = {
            'faultId': str(uuid.uuid4()),
            'timestamp': utils.current_time_str(),
            'message': response,
            'exceptions': [
                {
                    'exceptionType': 'ComplianceAuditSystems.Acabim.Exceptions.PythonException',
                    'stackTrace': stack_trace,
                    'message': exception_msg
                }
            ],
            'host': MessagingHandler.__get_host_info()
        }

        if req_message is not None and 'messageId' in req_message:
            fault_message['faultedMessageId'] = req_message['messageId']

        if queue in EXPECTED_MSG_TYPE:
            fault_message['faultMessageTypes'] = ['urn:message:{0}'.format(EXPECTED_MSG_TYPE[queue])]

        res_message['message'] = fault_message
        res_message['sentTime'] = utils.current_time_str()
        res_message['headers'] = {}
        res_message['host'] = MessagingHandler.__get_host_info()
        return bytes(json.dumps(res_message), 'utf8')

    @staticmethod
    def __get_host_info():
        return {'machineName': socket.gethostname(),
                'processName': f'ifcparser ({current_process().name}-{Thread.name})',
                'processId': os.getpid(),
                'pythonVersion': sys.version
                }

    @staticmethod
    def __get_header_properties():
        return pika.BasicProperties(content_type='application/vnd.masstransit+json')


def encode_file(path: str, content=None, ext=None, mime_type=None):
    size = os.path.getsize(path) if path else len(content) if content else 0

    if mime_type is None:
        from mimetypes import guess_type
        mime_type = guess_type(path)[0]

    if ext is None and path and not path.isspace():
        exts = os.path.splitext(path)
        ext = exts[1].lstrip('.') if len(exts) == 2 else 'txt'  # assume file type as txt if no type is found

    from base64 import b64encode
    data = None
    if path and not path.isspace():
        with open(path, 'rb') as file:
            data = b64encode(file.read())
    elif content:
        data = b64encode(content)

    return {
        "content": str(data, 'utf-8'),
        "encoding": 'base64',
        "extension": ext,
        "mimetype": mime_type,
        "size": size
    }


if __name__ == '__main__':
    import cas.configure as config

    config.configure_logging(['pika'])
    try:
        raise KeyError('I know')
    except KeyError as e:
        import traceback

        st = traceback.format_exc()
        print('done')
