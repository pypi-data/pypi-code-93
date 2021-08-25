import importlib
import os

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "load dev data"

    def handle(self, *args, **options):
        call_command("drop_tables")
        call_command("makemigrations")
        call_command("migrate")
        p = os.environ["DJANGO_SETTINGS_MODULE"].split(".")[0]
        fixtures = importlib.import_module(f"{p}.fixtures")
        fixtures.create_all()
        self.stdout.write(self.style.SUCCESS("Successfully created dev data"))
