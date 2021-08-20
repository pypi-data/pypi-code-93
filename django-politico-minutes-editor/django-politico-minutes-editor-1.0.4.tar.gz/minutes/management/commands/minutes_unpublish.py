import uuid

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from minutes.tasks.publish import unpublish
from minutes.models import Edition


class Command(BaseCommand):
    help = "Unpublishes an edition"

    def add_arguments(self, parser):
        parser.add_argument("edition", type=str)

    def handle(self, *args, **options):
        edition = options["edition"]
        if edition is not None:
            unpublish(str(Edition.objects.get(id=edition).id))
