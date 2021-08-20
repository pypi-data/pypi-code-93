from saleboxdjango.lib.api import get
from saleboxdjango.management.commands.lib.log import log
from saleboxdjango.models import KeyValueStore, SyncQueue


class SaleboxPullQueue:
    def __init__(self):
        self.config = self.get_config()
        self.sync_loop()

    def sync_loop(self):
        # create api call payload
        payload = {}
        for key in self.config:
            value = self.config[key]
            payload[key] = f"{value['created']}:{value['last_update']}"

        # request from api
        r = get('/api/v1/sync', payload)
        if r.status_code != 200:
            log('sync_pull_queue', f'API call failed, status: {r.status_code}, text: {r.text}', 'ERROR')
            return

        # process response
        response = r.json()
        for model_name in response['models']:
            self.update_queue(
                model_name,
                response['models'][model_name]['created'],
                response['models'][model_name]['last_update'],
                response['models'][model_name]['queue']
            )

        # loop again?
        if response['resync_now']:
            self.sync_loop()

    def get_config(self):
        # if we need to add new models in future, just add them to
        # this list here. it'll add them to the queue automatically
        models_to_sync = [
            'content_contentkeyvaluestore',
            'content_contentpage',
            'content_contentpageitem',
            'product_productcategory',
            'product_product',
            'product_productvariant',
        ]

        # generate base config
        config = {}
        for model in models_to_sync:
            config[model] = {
                'created': 0,
                'last_update': 0
            }

        # get kvs from db
        kvs = KeyValueStore.objects.filter(key='sync_config').first()
        if kvs is not None:
            config = {**config, **kvs.value}

        return config

    def save_config(self):
        kvs = KeyValueStore.objects.filter(key='sync_config').first()
        if kvs is None:
            KeyValueStore(key='sync_config', value=self.config).save()
        else:
            kvs.value = self.config
            kvs.save()

    def update_queue(self, model_name, created, last_update, queue):
        # loop through queue
        for model_id in queue:
            exists = SyncQueue \
                        .objects \
                        .filter(model_id=model_id) \
                        .filter(model_name=model_name) \
                        .count() > 0
            if not exists:
                try:
                    SyncQueue(
                        model_id=model_id,
                        model_name=model_name,
                    ).save()
                except:
                    log('sync_pull_queue', 'Error inserting SyncQueue into database', 'ERROR')
                    return

        # if successful, update the config values
        self.config[model_name]['created'] = created
        self.config[model_name]['last_update'] = last_update
        self.save_config()