# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-23 05:27
from __future__ import unicode_literals

from django.db import migrations


def populate_code(apps, schema_editor):
    from pretalx.common.mixins.models import GenerateCode

    User = apps.get_model("person", "User")
    for person in User.objects.all():
        person.code = GenerateCode.generate_code()
        person.save()


def empty_code(apps, schema_editor):
    User = apps.get_model("person", "User")
    User.objects.all().update(code=None)


class Migration(migrations.Migration):

    dependencies = [
        ("person", "0007_user_code"),
    ]

    operations = [
        migrations.RunPython(populate_code, empty_code),
    ]
