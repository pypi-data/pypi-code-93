import logging
from collections import defaultdict
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.files.storage import default_storage as storage
from django.core.management.base import BaseCommand
from django.db import models

# from django_extensions_too.management.color import color_style

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------

# https://gist.github.com/dvf/c103e697dab77c304d39d60cf279c500
def walk_folder(storage, base="/", error_handler=None):
    """
    Recursively walks a folder, using Django's File Storage.
    :param storage: <Storage>
    :param base: <str> The base folder
    :param error_handler: <callable>
    :yields: A tuple of base, subfolders, files
    """
    try:
        folders, files = storage.listdir(base)
    except OSError as e:
        logger.exception("An error occurred while walking directory %s", base)
        if error_handler:
            error_handler(e)
        return

    for subfolder in folders:
        # On S3, we don't really have subfolders, so exclude "."
        if subfolder == ".":
            continue

        new_base = str(Path(base, subfolder))
        yield from walk_folder(storage, new_base)
    yield base, folders, files


class Command(BaseCommand):
    help = "Deletes all files in MEDIA_ROOT that are not referenced in the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", help="Do not delete anything", action="store_true"
        )

    def handle(self, *args, **options):
        # self.style = color_style()

        # Get a list of all files under MEDIA_ROOT
        media = set()
        for base, subfolders, files in walk_folder(storage, "."):
            # print(base, subfolders, files)
            for f in files:
                path = Path(base) / Path(f)
                media.add(str(path))

        # Get list of all fields (value) for each model (key)
        # that is a FileField or subclass of a FileField
        model_dict = defaultdict(list)
        for model in apps.get_models():
            for field in model._meta.fields:
                if issubclass(field.__class__, models.FileField):
                    model_dict[model].append(field)

        # Get a list of all files referenced in the database
        referenced = set()
        for model, value in model_dict.items():
            all = model.objects.all().iterator()
            for object in all:
                for field in value:
                    target_file = getattr(object, field.name)
                    if target_file:
                        referenced.add(target_file.name)

        # Print each file in MEDIA_ROOT that is not referenced in the database
        not_referenced = media - referenced
        for f in not_referenced:
            if options["dry_run"]:
                logging.info("**DRY-RUN** would delete %s", f)
            else:
                storage.delete(f)
