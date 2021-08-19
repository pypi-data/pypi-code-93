from django.core.management.base import BaseCommand
from minutes.tasks.publish import publish
from minutes.models import Edition


class Command(BaseCommand):
    help = "Publishes an edition"

    def add_arguments(self, parser):
        parser.add_argument("edition", nargs="*", type=str)

    def handle(self, *args, **options):
        edition = (
            options["edition"][0] if len(options["edition"]) > 0 else None
        )

        if edition is not None:
            publish(str(Edition.objects.filter(live=True).get(id=edition).id))
        else:
            print("No valid edition id provided.".format(edition))
