# Generated by Django 2.0.3 on 2018-04-08 23:09

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import i18nfield.fields
import pretalx.common.mixins.models
import pretalx.event.models.organiser


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("event", "0012_auto_20180407_0814"),
    ]

    operations = [
        migrations.CreateModel(
            name="Organiser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("name", i18nfield.fields.I18nCharField(max_length=190)),
                (
                    "slug",
                    models.SlugField(
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="The slug may only contain letters, numbers, dots and dashes.",
                                regex="^[a-zA-Z0-9.-]+$",
                            )
                        ],
                    ),
                ),
            ],
            bases=(pretalx.common.mixins.models.LogMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=190)),
                ("all_events", models.BooleanField(default=False)),
                ("can_create_events", models.BooleanField(default=False)),
                ("can_change_teams", models.BooleanField(default=False)),
                ("can_change_organiser_settings", models.BooleanField(default=False)),
                ("can_change_event_settings", models.BooleanField(default=False)),
                ("can_change_submissions", models.BooleanField(default=False)),
                ("is_reviewer", models.BooleanField(default=False)),
                ("review_override_votes", models.PositiveIntegerField(default=0)),
                ("limit_events", models.ManyToManyField(blank=True, to="event.Event")),
                (
                    "members",
                    models.ManyToManyField(
                        related_name="teams", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "organiser",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teams",
                        to="event.Organiser",
                    ),
                ),
            ],
            bases=(pretalx.common.mixins.models.LogMixin, models.Model),
        ),
        migrations.CreateModel(
            name="TeamInvite",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                (
                    "token",
                    models.CharField(
                        blank=True,
                        default=pretalx.event.models.organiser.generate_invite_token,
                        max_length=64,
                        null=True,
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invites",
                        to="event.Team",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="event",
            name="organiser",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="events",
                to="event.Organiser",
            ),
        ),
    ]
