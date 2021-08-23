from datetime import datetime
from django.core.management.base import BaseCommand

from saleboxdjango.models import KeyValueStore
from saleboxdjango.management.commands.lib.log import log
from saleboxdjango.management.commands.lib.sync_pull_queue import SaleboxPullQueue
from saleboxdjango.management.commands.lib.sync_pull_models import SaleboxPullModels
from saleboxdjango.management.commands.lib.sync_pull_posimages import SaleboxPullPOSImages


class Command(BaseCommand):
    def handle(self, *args, **options):
        if self.sync_in_progress():
            print('Bailing out: sync is in progress')
            return

        # start
        log('core', 'saleboxsync2 starting')
        self.set_sync_in_progress(True)

        # do stuff
        SaleboxPullQueue()
        SaleboxPullModels()
        SaleboxPullPOSImages()

        # done
        log('core', 'saleboxsync2 completed successfully')
        self.set_sync_in_progress(False)

    def sync_in_progress(self):
        kvs = KeyValueStore.objects.filter(key='sync_in_progress').first()

        # first time here? create the keyvalue record
        if kvs is None:
            self.set_sync_in_progress(False)
            return False

        # if sync is in progress, did it start long enough ago to
        # assume it failed?
        if kvs.value['sync_in_progress']:
            diff = datetime.utcnow().timestamp() - kvs.value['last_seen']
            if diff > 300: # 5 minutes
                log('core', 'saleboxsync2 sync_in_progress timeout', 'WARNING')
                return False

        # fallback
        return kvs.value['sync_in_progress']

    def set_sync_in_progress(self, sync_in_progress):
        # create new value
        value = {
            'sync_in_progress': sync_in_progress,
            'last_seen': datetime.utcnow().timestamp()
        }

        # retrieve from the db
        kvs = KeyValueStore.objects.filter(key='sync_in_progress').first()
        if kvs is None:
            KeyValueStore(key='sync_in_progress', value=value).save()
        else:
            kvs.value = value
            kvs.save()