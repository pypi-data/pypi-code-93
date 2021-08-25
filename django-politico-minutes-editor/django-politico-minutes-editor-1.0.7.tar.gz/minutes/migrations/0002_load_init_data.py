from django.db import migrations, IntegrityError, transaction
import os
from django.core import serializers


fixture_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../fixtures")
)
fixture_filename = "init.json"


def load_fixture(apps, schema_editor):
    fixture_file = os.path.join(fixture_dir, fixture_filename)

    fixture = open(fixture_file, "rb")
    objects = serializers.deserialize("json", fixture, ignorenonexistent=True)
    for obj in objects:
        try:
            with transaction.atomic():
                obj.save()
        except IntegrityError:
            pass
    fixture.close()


def unload_fixture(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("minutes", "0001_initial")]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture)
    ]
