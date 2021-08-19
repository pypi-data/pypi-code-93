from django.db import models

from huscy.projects.models import Project


class EMail(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    text = models.TextField()
    footer = models.TextField()

    class Meta:
        abstract = True


class InvitationEMail(EMail):
    class Meta:
        verbose_name = 'Invitation email'
        verbose_name_plural = 'Invitation emails'


class ReminderEMail(EMail):
    class Meta:
        verbose_name = 'Reminder email'
        verbose_name_plural = 'Reminder emails'
