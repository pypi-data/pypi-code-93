from django.core.management.base import BaseCommand
from minutes.tasks.publish import autopublisher


class Command(BaseCommand):
    help = "Publishes an edition"

    def add_arguments(self, parser):
        parser.add_argument("edition", nargs="*", type=str)

    def handle(self, *args, **options):
        autopublisher()
