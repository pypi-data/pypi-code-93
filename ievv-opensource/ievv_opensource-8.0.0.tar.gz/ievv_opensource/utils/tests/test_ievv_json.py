import datetime
import decimal

import arrow
from django import test
from django.conf import settings
from model_bakery import baker

from ievv_opensource.utils import ievv_json


class TestIevvJSON(test.TestCase):
    def test_datetime(self):
        data = {'somedatetime': arrow.get(datetime.datetime(2019, 12, 23, 23, 50), 'Asia/Tokyo').datetime}
        encoded = ievv_json.dumps(data, sort_keys=True)
        self.assertEquals(encoded, '{"somedatetime": {"__type__": "datetime", "value": "2019-12-23 23:50:00+09:00"}}')
        decoded = ievv_json.loads(encoded)
        self.assertDictEqual(decoded, data)

    def test_date(self):
        data = {'somedate': datetime.date(2019, 12, 24)}
        encoded = ievv_json.dumps(data, sort_keys=True)
        self.assertEquals(encoded, '{"somedate": {"__type__": "date", "value": "2019-12-24"}}')
        decoded = ievv_json.loads(encoded)
        self.assertDictEqual(decoded, data)

    def test_time(self):
        data = {'sometime': datetime.time(12, 40, 38, 123)}
        encoded = ievv_json.dumps(data, sort_keys=True)
        self.assertEquals(encoded, '{"sometime": {"__type__": "time", "value": "12:40:38.000123"}}')
        decoded = ievv_json.loads(encoded)
        self.assertDictEqual(decoded, data)

    def test_decimal(self):
        data = {'somedecimal': decimal.Decimal('10.2')}
        encoded = ievv_json.dumps(data, sort_keys=True)
        self.assertEquals(encoded, '{"somedecimal": {"__type__": "decimal", "value": "10.2"}}')
        decoded = ievv_json.loads(encoded)
        self.assertDictEqual(decoded, data)

    def test_djangomodel(self):
        user = baker.make(settings.AUTH_USER_MODEL)
        data = {'someuser': user}
        encoded = ievv_json.dumps(data, sort_keys=True)
        self.assertEquals(
            encoded,
            '{"someuser": {"__model__": "auth.User", "__type__": "djangomodel", "value": %s}}' % (user.id,))
        decoded = ievv_json.loads(encoded)
        self.assertEqual(decoded, {
            'someuser': {'__model__': 'auth.User', '__type__': 'djangomodel', 'value': user.id}})
