# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-23 05:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("person", "0006_user_get_gravatar"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="code",
            field=models.CharField(max_length=16, null=True, unique=True),
        ),
    ]
