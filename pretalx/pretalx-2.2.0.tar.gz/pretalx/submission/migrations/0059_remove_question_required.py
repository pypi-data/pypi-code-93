# Generated by Django 3.1.4 on 2021-06-24 17:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0058_question_required_data"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="question",
            name="required",
        ),
    ]
