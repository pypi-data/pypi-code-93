from django.core.management.base import BaseCommand
from django.conf import settings
from minutes.utils.aws_lambda import invoke


class Command(BaseCommand):
    help = "Publishes an edition"

    def handle(self, *args, **options):
        resp = invoke({
          "body": {
            "manual": True,
            "testing": True,
            "token": settings.MINUTES_BAKERY_TOKEN,
            "mode": "STAGING",
            "verticalSlug": "congress",
            "editionId": "3fe5f12a-425d-41a1-878f-28ddc07e4995"
          }
        })

        print(resp.ok)
        print(resp.body)
