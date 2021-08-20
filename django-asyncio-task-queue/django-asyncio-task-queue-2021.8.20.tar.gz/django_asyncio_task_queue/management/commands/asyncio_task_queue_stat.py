from django.apps import apps
from django.core.management.base import BaseCommand

from ...utils import get_models

class Command(BaseCommand):
    def handle(self, *args, **options):
        for model in get_models():
            model.refresh_stat()
