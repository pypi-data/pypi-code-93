from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.translation import gettext as _
from model_utils.models import TimeStampedModel


class Activity(TimeStampedModel):
    CREATE = "create"
    UPDATE = "update"
    ACTION_CHOICES = (
        (CREATE, _("Create")),
        (UPDATE, _("Update")),
    )

    target_content_type = models.ForeignKey(
        ContentType,
        related_name='activity',
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name=_('Content Type'),
    )
    target_object_id = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_('Target Object ID'),
    )
    target = GenericForeignKey('target_content_type', 'target_object_id')
    action = models.CharField(
        verbose_name=_("Action"),
        max_length=50,
        choices=ACTION_CHOICES,
    )
    by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("By User"),
        on_delete=models.CASCADE,
    )
    data = models.JSONField(verbose_name=_("Data"))
    change = models.JSONField(verbose_name=_("Change"), blank=True)

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = _("Activities")

    def __str__(self):
        return "{} {} {}".format(self.by_user, self.action, self.target)

    def by_user_display(self):
        by_user = str(self.by_user)
        if not by_user.strip():
            by_user = self.by_user.email
        return by_user

    def get_display(self):
        if self.action == Activity.CREATE:
            return _('Created')
        elif self.action == Activity.UPDATE:
            titles = []
            try:
                for field in self.change.keys():
                    try:
                        target_field = self.target._meta.get_field(field)
                        if hasattr(target_field, "verbose_name"):
                            field_name = target_field.verbose_name
                        else:
                            field_name = field
                        titles.append(str(field_name))
                    except FieldDoesNotExist:
                        continue
            except AttributeError:
                titles.append("unknown")

            return _('Changed {}').format(', '.join(titles))
        else:
            raise NotImplementedError
