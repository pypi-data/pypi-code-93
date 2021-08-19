from datetime import datetime, timedelta
from .connection import Connection

from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class PublicClient:
    def __init__(self):
        self.connection = Connection(None, None)

    def health(self):
        return self.connection.get('/v1/gethealth')

    def markets(self):
        return self.connection.get('/v1/markets')

    def board(self, product_code='BTC_JPY'):
        return self.connection.get('/v1/board', product_code=product_code)

    def ticker(self, product_code='BTC_JPY'):
        return self.connection.get('/v1/ticker', product_code=product_code)

    def executions(self, product_code='BTC_JPY', count=None, before=None, after=None):
        query = dict(
            product_code=product_code,
            count=count,
            before=before,
            after=after,
        )
        query = {k: v for k, v in query.items() if v is not None}
        return self.connection.get('/v1/executions', query)

    def chats(self, from_date=None):
        if not from_date:
            from_date = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        return self.connection.get('/v1/getchats', from_date=from_date).body
