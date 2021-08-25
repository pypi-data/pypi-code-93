from django.core.management.base import BaseCommand

from view_models import utils

class Command(BaseCommand):
    '''
    Refreshes all materialized views (subclasses of MaterializedViewModel).
    '''
    def handle(self, **kwargs):
        utils.refresh_views()