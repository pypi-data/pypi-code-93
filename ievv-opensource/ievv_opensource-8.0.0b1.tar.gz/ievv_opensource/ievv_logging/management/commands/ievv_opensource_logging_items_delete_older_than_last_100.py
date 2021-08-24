import sys
import traceback

from django.core.management.base import BaseCommand

from ievv_opensource.ievv_logging.utils import IevvLogging
from ievv_opensource.ievv_logging.models import IevvLoggingEventBase


def delete_older_than_the_last_100():
    logmessages = []
    for loggingeventbase in IevvLoggingEventBase.objects.all():
        last_created_item_ids = loggingeventbase.ievvloggingeventitem_set.all()[:100].values_list('id', flat=True)
        items = loggingeventbase.ievvloggingeventitem_set.exclude(pk__in=list(last_created_item_ids))
        logmsg = f'Deleting {items.count()} for {loggingeventbase.slug}'
        sys.stdout.write(f'{logmsg}\n')
        logmessages.append(logmsg)
        items.delete()
    return logmessages


class Command(BaseCommand):
    help = 'Deletes IevvLoggingEventItem rows for each IevvLoggingEventBase except the last 100.'

    def handle(self, *args, **options):
        ievvlogging = IevvLogging(__name__)
        ievvlogging.begin()
        try:
            logmessages = delete_older_than_the_last_100()
        except Exception:
            ievvlogging.finish(
                error_occured=True,
                error=traceback.format_exc()
            )
        else:
            ievvlogging.finish(logmessages=logmessages)
