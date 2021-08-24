from collections import defaultdict

from django.core.files.storage import default_storage as storage
from django.core.management.base import BaseCommand
from django.db import models

# from django_extensions_too.management.color import color_style

# -----------------------------------------------------------------------------


def get_apps_from_cache():
    try:
        from django.apps import apps

        return [
            app.models_module for app in apps.get_app_configs() if app.models_module
        ]
    except ImportError:
        from django.db.models.loading import cache

        return cache.get_apps()


def get_models_from_cache(app):
    try:
        from django.apps import apps

        return apps.get_models(app)
    except ImportError:
        from django.db.models.loading import cache

        return cache.get_models(app)


# -----------------------------------------------------------------------------


class Command(BaseCommand):
    help = "Prints a list of all files referenced in the database, but are missing in MEDIA_ROOT."

    def handle(self, *args, **options):
        # self.style = color_style()

        file_list = []

        # Get list of all fields (value) for each model (key)
        # that is a FileField or subclass of a FileField
        model_dict = defaultdict(list)
        for app in get_apps_from_cache():
            for model in get_models_from_cache(app):
                for field in model._meta.fields:
                    if issubclass(field.__class__, models.FileField):
                        model_dict[model].append(field)

        # Get a list of all files missing in MEDIA_ROOT
        for model, value in model_dict.items():
            all = model.objects.all().iterator()
            for object in all:
                for field in value:
                    target_file = getattr(object, field.name)
                    if target_file:
                        file_list.append(target_file.name)

        # Print list of missing files
        file_list = sorted(list(set(file_list)))
        for f in file_list:
            if not storage.exists(f):
                print(f)
