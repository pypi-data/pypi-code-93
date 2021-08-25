from django.core.management.base import BaseCommand

from view_models import utils

class Command(BaseCommand):
    '''
    Creates or replaces all views (subclasses of ViewModel or MaterializedViewModel).
    Does not refresh MaterializedViewModel subclasses - use refresh_view_models for that.
    '''
    def handle(self, **kwargs):
        utils.create_views()