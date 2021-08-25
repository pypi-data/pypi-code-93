from django.core.management.base import BaseCommand

from ... import utils

class Command(BaseCommand):
    '''
    Shortcut for running create_view_models and refresh_view_models.
    '''
    def handle(self, **kwargs):
        utils.sync_views()