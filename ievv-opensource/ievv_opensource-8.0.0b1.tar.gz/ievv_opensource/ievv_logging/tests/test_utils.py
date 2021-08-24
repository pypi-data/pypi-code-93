import traceback
from datetime import datetime, timedelta

from django import test
from ievv_opensource.ievv_logging.models import IevvLoggingEventBase, IevvLoggingEventItem
from ievv_opensource.ievv_logging.utils import IevvLogging, getDuration


class TestIevvLogging(test.TestCase):

    def test_begin(self):
        ievvlogging = IevvLogging('foo_bar')
        ievvlogging.begin()
        self.assertEqual(1, IevvLoggingEventBase.objects.count())
        self.assertEqual(1, IevvLoggingEventItem.objects.count())

    def test_finish(self):
        ievvlogging = IevvLogging('foo_bar')
        ievvlogging.begin()
        self.assertEqual(1, IevvLoggingEventBase.objects.count())
        self.assertEqual(1, IevvLoggingEventItem.objects.count())
        ievvlogging.finish()
        self.assertEqual(1, IevvLoggingEventBase.objects.count())
        self.assertEqual(1, IevvLoggingEventItem.objects.count())

    def test_that_no_duplicates_of_slug_is_created(self):
        ievvlogging = IevvLogging('foo_bar')
        ievvlogging.begin()
        ievvlogging2 = IevvLogging('foo_bar')
        ievvlogging2.begin()
        self.assertEqual(1, IevvLoggingEventBase.objects.count())

    def test_each_logging_gives_another_row_in_item_model(self):
        ievvlogging = IevvLogging('foo_bar')
        ievvlogging.begin()
        ievvlogging.finish()
        ievvlogging2 = IevvLogging('foo_bar')
        ievvlogging2.begin()
        ievvlogging2.finish()
        self.assertEqual(1, IevvLoggingEventBase.objects.count())
        self.assertEqual(2, IevvLoggingEventItem.objects.count())

    def test_jsondata_populating(self):
        ievvlogging = IevvLogging('foo_bar')
        ievvlogging.begin()
        a_dictionary = {'a': 'b'}
        ievvlogging.finish(
            foo=1,
            bar=2,
            **a_dictionary
        )
        self.assertTrue('a' in IevvLoggingEventItem.objects.first().data)
        self.assertEqual(3, len(IevvLoggingEventItem.objects.first().data))

    def test_success_run_is_NOT_set(self):
        ievvlogging = IevvLogging('foo')
        ievvlogging.begin()
        ievvlogging.finish()
        self.assertTrue(IevvLoggingEventItem.objects.first().success_run)
        self.assertIsNotNone(IevvLoggingEventItem.objects.first().success_run)

    def test_success_run_is_false(self):
        ievvlogging = IevvLogging('foo')
        ievvlogging.begin()
        ievvlogging.finish(error_occured=True)
        self.assertFalse(IevvLoggingEventItem.objects.first().success_run)

    def test_success_is_false_and_exception_msg_is_saved_in_data(self):
        ievvlogging = IevvLogging('foo')
        ievvlogging.begin()
        try:
            {'foo': 11}['bar']
        except Exception:
            ievvlogging.finish(
                error_occured=True,
                error=traceback.format_exc()
            )
        else:
            ievvlogging.finish()
        loggingitem = IevvLoggingEventItem.objects.first()
        self.assertFalse(loggingitem.success_run)
        self.assertTrue('error' in loggingitem.data)
        self.assertTrue('KeyError' in loggingitem.data['error'])

    def test_NO_error_occured_is_set_and_exception_msg_is_saved_in_data(self):
        # same test as above, but with no error
        ievvlogging = IevvLogging('foo')
        ievvlogging.begin()
        try:
            {'foo': 11}['foo']
        except Exception:
            ievvlogging.finish(
                error_occured=True,
                error=traceback.format_exc()
            )
        else:
            ievvlogging.finish()
        loggingitem = IevvLoggingEventItem.objects.first()
        self.assertTrue(loggingitem.success_run)
        self.assertFalse('error' in loggingitem.data)

    def test_duration_less_than_a_second(self):
        to_time = datetime.now()
        from_time = to_time - timedelta(milliseconds=100)
        duration = getDuration(from_dt=from_time, to_dt=to_time)
        self.assertEqual('Less than a second', duration)

    def test_duration_some_seconds(self):
        to_time = datetime.now()
        from_time = to_time - timedelta(seconds=33)
        duration = getDuration(from_dt=from_time, to_dt=to_time)
        duration_seconds = getDuration(from_dt=from_time, to_dt=to_time, interval='seconds')
        self.assertEqual('0 hours, 0 minutes and 33 seconds', duration)
        self.assertEqual(33, duration_seconds)

    def test_duration_some_minutes(self):
        to_time = datetime.now()
        from_time = to_time - timedelta(minutes=45)
        duration = getDuration(from_dt=from_time, to_dt=to_time)
        duration_seconds = getDuration(from_dt=from_time, to_dt=to_time, interval='seconds')
        self.assertEqual('0 hours, 45 minutes and 0 seconds', duration)
        self.assertEqual(45*60, duration_seconds)

    def test_duration_some_minutes_and_seconds(self):
        to_time = datetime.now()
        from_time = to_time - timedelta(minutes=45)
        from_time = from_time - timedelta(seconds=15)
        duration = getDuration(from_dt=from_time, to_dt=to_time)
        self.assertEqual('0 hours, 45 minutes and 15 seconds', duration)

    def test_duration_some_hours(self):
        to_time = datetime.now()
        from_time = to_time - timedelta(hours=5)
        duration = getDuration(from_dt=from_time, to_dt=to_time)
        duration_seconds = getDuration(from_dt=from_time, to_dt=to_time, interval='seconds')
        self.assertEqual('5 hours, 0 minutes and 0 seconds', duration)
        self.assertEqual(5*60*60, duration_seconds)

    def test_duration_some_hours_minutes_and_seconds(self):
        to_time = datetime.now()
        from_time = to_time - timedelta(hours=5)
        from_time = from_time - timedelta(minutes=22)
        from_time = from_time - timedelta(seconds=15)
        duration = getDuration(from_dt=from_time, to_dt=to_time)
        self.assertEqual('5 hours, 22 minutes and 15 seconds', duration)

    def test_duration_some_days_hours_minutes_and_seconds(self):
        to_time = datetime.now()
        from_time = to_time - timedelta(days=15)
        from_time = from_time - timedelta(hours=22)
        from_time = from_time - timedelta(minutes=22)
        from_time = from_time - timedelta(seconds=15)
        duration = getDuration(from_dt=from_time, to_dt=to_time)
        self.assertEqual('15 days, 22 hours, 22 minutes and 15 seconds', duration)

    def test_duration_some_months_days_hours_minutes_and_seconds(self):
        to_time = datetime.now()
        from_time = to_time - timedelta(days=365*2)
        from_time = from_time - timedelta(hours=2)
        from_time = from_time - timedelta(minutes=2)
        from_time = from_time - timedelta(seconds=2)
        duration = getDuration(from_dt=from_time, to_dt=to_time)
        self.assertTrue('years' in duration)


