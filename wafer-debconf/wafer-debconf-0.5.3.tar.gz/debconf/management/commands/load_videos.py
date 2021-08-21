from django.core.management.base import BaseCommand
from wafer.talks.models import Talk

import datetime
import os
import requests


class Command(BaseCommand):
    help = 'Load video URLs from sreview.debian.net'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sreview-url', metavar='URL', type=str,
            default='https://sreview.debian.net/released.json',
            help='URL for the released.json file in the SReview instance',
        )

        current_year = datetime.datetime.today().year
        parser.add_argument(
            '--base-url', metavar='URL', type=str,
            default='https://meetings-archive.debian.net/pub/debian-meetings/%s' % current_year,
            help='Base URL for the videos released by sreview',
        )

        parser.add_argument(
            '--dry-run', action='store_true',
            help='Only show what would be done',
        )

    def handle(self, *args, **options):
        jsonurl = options['sreview_url']

        jsondata = requests.get(jsonurl)
        jsondata.raise_for_status()

        data = jsondata.json()

        baseurl = options['base_url'].rstrip("/")

        for entry in data['videos']:
            talk_id = int(entry['eventid'])
            talk = Talk.objects.get(pk=talk_id)
            url = baseurl + "/" + entry['video'].lstrip("/")
            if options['dry_run']:
                print('Would load video for <%s>: %s' % (talk, url))
            else:
                talk.urls.update_or_create(
                    description='Video',
                    defaults={
                        "url": url,
                    }
                )
                print('Loaded video for <%s>: %s' % (talk, url))
