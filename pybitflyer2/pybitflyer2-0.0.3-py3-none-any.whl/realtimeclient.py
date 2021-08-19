import websocket
from threading import Thread
import time
import hmac
import json

from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class RealtimeClient:
    from itertools import product
    PUBLIC_EVENT_NAMES = ['lightning_board_snapshot', 'lightning_board', 'lightning_ticker', 'lightning_executions']
    MARKETS = ['BTC_JPY', 'XRP_JPY', 'ETH_JPY', 'XLM_JPY', 'MONA_JPY',
               'ETH_BTC', 'BCH_BTC', 'FX_BTC_JPY', 'BTCJPY_MAT1WK', 'BTCJPY_MAT2WK', 'BTCJPY_MAT3M']
    PUBLIC_CHANNEL_NAMES = list(map(lambda x: f"{x[0]}_{x[1]}", product(PUBLIC_EVENT_NAMES, MARKETS)))
    PRIVATE_CHANNEL_NAMES = ['child_order_events', 'parent_order_events']
    ON_EVENT_NAMES = ['open', 'message', 'error', 'close', 'ping', 'pong']

    def __init__(self, key=None, secret=None):
        self.endpoint = 'wss://ws.lightstream.bitflyer.com/json-rpc'
        self.ws = websocket.WebSocketApp(
            self.endpoint,
            on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close,
            on_ping=self.on_ping, on_pong=self.on_pong,
        )
        self.public_channel_handlers = {}
        self.private_channel_handlers = {}
        self.event_handlers = {}
        self._JSONRPC_ID_AUTH = 1
        self._key = key
        self._secret = secret

    def subscribe(self, channel, handler):
        logger.info(f"Adding subscribe handler for channgel:{channel}")
        if channel in self.PUBLIC_CHANNEL_NAMES:
            self.public_channel_handlers[channel] = handler
        elif channel in self.PRIVATE_CHANNEL_NAMES:
            if not (self._key and self._secret):
                raise Exception(f"Must set key and secret when subscribe private channel '{channel}'")
            self.private_channel_handlers[channel] = handler
        else:
            raise Exception(f"Channel name '{channel}' is not supported.")

    def on(self, event_name, handler):
        logger.info(f"Adding event handler for channgel:{event_name}")
        if event_name in self.ON_EVENT_NAMES:
            self.event_handlers[event_name] = handler
        else:
            raise Exception(f"Event name '{event_name}' is not supported.")

    def notify_event(self, event_name, *args):
        handler = self.event_handlers.get(event_name, lambda x: None)
        if len(args) != 0:
            handler(*args)
        else:
            handler()

    def start(self):
        logger.info(f"start thread")
        websocketThread = Thread(target=self.run, args=(self.ws, ))
        websocketThread.start()

    def run(self, ws):
        logger.info(f"run websocket")
        while True:
            ws.run_forever(ping_interval=30, ping_timeout=10)
            time.sleep(3)

    def on_open(self, ws):
        logger.info("Websocket connected")
        if len(self.public_channel_handlers.keys()) > 0:
            logger.info(f"send public channgel subscribe request")
            params = [dict(method='subscribe', params=dict(channel=c)) for c in self.public_channel_handlers.keys()]
            self.ws.send(json.dumps(params))

        if len(self.private_channel_handlers.keys()) > 0:
            self.auth(ws)

        self.notify_event('open')

    def auth(self, ws):
        from hashlib import sha256
        from secrets import token_hex
        now = int(time.time())
        nonce = token_hex(16)
        sign = hmac.new(
            self._secret.encode('utf-8'),
            ''.join([str(now), nonce]).encode('utf-8'),
            sha256).hexdigest()
        params = {
            'method': 'auth',
            'params': {
                'api_key': self._key, 'timestamp': now,
                'nonce': nonce, 'signature': sign
            },
            'id': self._JSONRPC_ID_AUTH
        }

        logger.info(f"send auth")
        ws.send(json.dumps(params))

    def subscribe_channels(self):
        if len(self.public_channel_handlers.keys()) > 0:
            params = [dict(method='subscribe', params=dict(channel=c)) for c in self.public_channel_handlers.keys()]
            self.ws.send(json.dumps(params))

        if len(self.private_channel_handlers.keys()) > 0:
            params = [dict(method='subscribe', params=dict(channel=c)) for c in self.private_channel_handlers.keys()]
            self.ws.send(json.dumps(params))

    def on_error(self, ws, error):
        logger.warn(f"error: {str(error)}")
        self.notify_event('error', error)

    def on_close(self, ws, close_status_code, close_msg):
        logger.info(f"Websocket closed. close_status_code:{close_status_code} close_msg:{close_msg}")
        self.notify_event('close')

    def on_message(self, ws, raw):
        logger.info('Message received')
        msg = json.loads(raw)
        logger.debug(msg)
        # {'jsonrpc': '2.0',
        # 'method': 'channelMessage',
        # 'params': {'channel': 'lightning_ticker_BTC_JPY',
        #            'message': {'best_ask': 4881653.0,
        #                        (snip)
        #                        'volume_by_product': 3875.54913354}}}
        # {'error': {'code': -32600, 'data': 'Empty Array', 'message': 'Invalid Request'},
        #  'id': None,
        #  'jsonrpc': '2.0'}
        # {'id': 1, 'jsonrpc': '2.0', 'result': True}
        # {'jsonrpc': '2.0',
        #  'method': 'channelMessage',
        # ' params': {'channel': 'child_order_events',
        #             'message': [{'child_order_acceptance_id': 'JRF20210812-163510-972289',
        #                          'child_order_id': 'JOR20210812-163511-122385H',
        #                          'child_order_type': 'LIMIT',
        #                          'event_date': '2021-08-12T16:35:11.0580713Z',
        #                          'event_type': 'ORDER',
        #                          'expire_date': '2021-09-11T16:35:10',
        #                          'price': 320000,
        #                          'product_code': 'ETH_JPY',
        #                          'side': 'BUY',
        #                          'size': 0.01}]}}
        # {'jsonrpc': '2.0',
        #  'method': 'channelMessage',
        #  'params': {'channel': 'child_order_events',
        #             'message': [{'child_order_acceptance_id': 'JRF20210812-163510-972289',
        #                          'child_order_id': 'JOR20210812-163511-122385H',
        #                          'event_date': '2021-08-12T16:35:46.6576528Z',
        #                          'event_type': 'CANCEL',
        #                          'price': 320000,
        #                          'product_code': 'ETH_JPY',
        #                          'size': 0.01}]}}
        if 'id' in msg and msg['id'] == self._JSONRPC_ID_AUTH:
            if 'error' in msg:
                logger.critical('auth error: {}'.format(msg["error"]))
            elif msg.get('result', None):
                logger.info("auth success")
                if len(self.private_channel_handlers.keys()) > 0:
                    params = [dict(method='subscribe', params=dict(channel=c)) for c in self.private_channel_handlers.keys()]
                    logger.info(f"send private channgel subscribe request")
                    self.ws.send(json.dumps(params))

        if msg['method'] == 'channelMessage':
            channel = msg['params']['channel']
            message = msg['params']['message']
            handler = self.public_channel_handlers.get(channel, lambda x: None)
            handler(message)
        else:
            logger.info("Unhandled message")

        self.notify_event('message', msg)

    def on_ping(self, wsapp, message):
        logger.info("Got a ping")
        self.notify_event('ping', message)

    def on_pong(self, wsapp, message):
        logger.info("Got a pong")
        self.notify_event('pong', message)
