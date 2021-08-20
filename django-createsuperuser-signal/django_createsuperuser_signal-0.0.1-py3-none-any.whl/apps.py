from django.apps import AppConfig
from django.db.models.signals import post_migrate

from createsuperuser.signals import create_superuser


class CreatesuperuserConfig(AppConfig):
    name = ''

    def ready(self):
        post_migrate.connect(create_superuser, sender=self)