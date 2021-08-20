from django.db import models

class Command(models.Model):
    app = models.TextField()
    name = models.TextField(unique=True)
    is_enabled = models.BooleanField(default=True,verbose_name='enabled')

    class Meta:
        db_table = 'django_command_debug_command'
        indexes = [
           models.Index(fields=['app',]),
           models.Index(fields=['name',]),
        ]
        ordering = ('name',)
