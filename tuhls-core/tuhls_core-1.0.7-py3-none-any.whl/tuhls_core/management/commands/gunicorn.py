import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from plumbum import FG, local


class Command(BaseCommand):
    help = "start prod server"

    def handle(self, *args, **options):
        call_command("collectstatic", "--no-input")
        call_command("migrate")
        p = os.environ["DJANGO_SETTINGS_MODULE"].split(".")[0]
        (
            local.get(".venv/bin/gunicorn")[
                "--bind",
                settings.GUNICORN_BIND,
                f"--workers={settings.GUNICORN_WORKERS}",
                "-k",
                "egg:meinheld#gunicorn_worker",
                "--worker-tmp-dir",
                "/dev/shm",
                f"{p}.base.wsgi:application",
            ]
            & FG
        )
