# Generated by Django 3.0.3 on 2020-03-04 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0045_extend_question_help_text_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="submission_types",
            field=models.ManyToManyField(
                blank=True, related_name="questions", to="submission.SubmissionType"
            ),
        ),
    ]
