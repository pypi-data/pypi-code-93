from django import test

from ievv_opensource.ievv_logging.management.commands.ievv_opensource_logging_items_delete_older_than_last_100 import \
    delete_older_than_the_last_100
from ievv_opensource.ievv_logging.models import IevvLoggingEventBase, IevvLoggingEventItem
from ievv_opensource.ievv_logging.utils import IevvLogging


class TestManagmentScriptThatCleansOldLoggingItems(test.TestCase):

    def test_management_script_one_slug_only(self):
        # Make 105 log items
        for i in range(105):
            ievvlogging = IevvLogging('foo_bar')
            ievvlogging.begin()
            ievvlogging.finish()
        # check that we have in fact 105
        self.assertEqual(105, IevvLoggingEventItem.objects.count())
        # check that the last is the first created
        self.assertEqual(1, IevvLoggingEventItem.objects.last().id)
        # run the clean script
        delete_older_than_the_last_100()
        # check that count is now 100
        self.assertEqual(100, IevvLoggingEventItem.objects.count())
        # check that the last created still exists
        self.assertEqual(105, IevvLoggingEventItem.objects.first().id)
        # check that the oldest no longer exist
        with self.assertRaises(IevvLoggingEventItem.DoesNotExist):
            IevvLoggingEventItem.objects.get(pk=1)

    def test_management_script_with_multiple_slugs(self):
        # make more than 100 for multiple slugs
        sluglist = ['foo', 'bar', 'baz']
        for slug in sluglist:
            for i in range(115):
                ievvlogging = IevvLogging(slug)
                ievvlogging.begin()
                ievvlogging.finish()
        delete_older_than_the_last_100()
        # check that the number in database after cleaning is number of slugs times 100
        self.assertEqual(100*len(sluglist), IevvLoggingEventItem.objects.count())

