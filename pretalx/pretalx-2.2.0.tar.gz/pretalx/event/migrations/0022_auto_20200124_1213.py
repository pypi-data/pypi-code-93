# Generated by Django 2.2.9 on 2020-01-24 12:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("event", "0021_auto_20190429_0750"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organiser",
            name="slug",
            field=models.SlugField(
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="The slug may only contain letters, numbers, dots and dashes.",
                        regex="^[a-zA-Z0-9-]+$",
                    )
                ],
            ),
        ),
    ]
