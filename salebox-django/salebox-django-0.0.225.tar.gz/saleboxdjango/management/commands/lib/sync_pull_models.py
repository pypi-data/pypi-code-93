from django.db.models import Count

from saleboxdjango.lib.api import get
from saleboxdjango.management.commands.lib.log import log
from saleboxdjango.management.commands.lib.models.contentkeyvaluestore import sync_contentkeyvaluestore
from saleboxdjango.management.commands.lib.models.contentpage import sync_contentpage
from saleboxdjango.management.commands.lib.models.contentpageitem import sync_contentpageitem
from saleboxdjango.management.commands.lib.models.productcategory import sync_productcategory
from saleboxdjango.management.commands.lib.models.product import sync_product
from saleboxdjango.management.commands.lib.models.productvariant import sync_productvariant

from saleboxdjango.models import SyncQueue


class SaleboxPullModels:
    def __init__(self):
        self.error = False

        # retreive summary of queue size
        items_in_queue, config = self.retrieve_queue_size()
        if not items_in_queue:
            return

        # set dependency levels, i.e. items in level 1 depend on level 0, level 2 on level 1, etc
        groups = self.get_dependency_groups()
        for level in groups:
            for model_name in level:
                if model_name in config and config[model_name] > 0 and not self.error:
                    self.sync_models(model_name)

    def get_dependency_groups(self):
        one = [
            'content_contentkeyvaluestore',
            'content_contentpage',
            'product_productcategory',
        ]

        two = [
            'content_contentpageitem',
            'product_product',
        ]

        three = [
            'product_productvariant',
        ]

        return [one, two, three]

    def retrieve_queue_size(self):
        data = SyncQueue \
                .objects \
                .values('model_name') \
                .annotate(count=Count('model_name')) \
                .order_by('model_name') \
                .values_list('model_name', 'count')

        output = {}
        total = 0
        for d in data:
            output[d[0]] = d[1]
            total += d[1]

        return (total > 0, output)

    def sync_models(self, model_name):
        function = {
            'content_contentkeyvaluestore': sync_contentkeyvaluestore,
            'content_contentpage': sync_contentpage,
            'content_contentpageitem': sync_contentpageitem,
            'product_productcategory': sync_productcategory,
            'product_product': sync_product,
            'product_productvariant': sync_productvariant,
        }

        queue_ids = SyncQueue \
                        .objects \
                        .filter(model_name=model_name) \
                        .order_by('created') \
                        .values_list('model_id', flat=True)

        # spit queue into batches of 100, then process each batch in turn
        batch_size = 100
        queue_id_batches = [queue_ids[i * batch_size:(i + 1) * batch_size] for i in range((len(queue_ids) + batch_size - 1) // batch_size )]
        for batch in queue_id_batches:
            path = f"/api/v1/sync/{model_name.replace('_', '-')}"
            r = get(path, {'id': ','.join(batch)})
            if r.status_code != 200:
                log('sync_pull_models', f'API call failed: {path} status: {r.status_code}', 'ERROR')
                self.error = True
                return

            # process objects returned from the api
            response = r.json()
            for o in response['objects']:
                function[response['model']](o)

            # remove all completed items from the queue
            SyncQueue \
                .objects \
                .filter(model_name=model_name) \
                .filter(model_id__in=batch) \
                .delete()
