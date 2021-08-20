from django.db import models

class Config(models.Model):
    app_label = models.CharField(max_length=255)
    label = models.CharField(max_length=255,unique=True)

    push_limit = models.IntegerField(default=42)

    class Meta:
        db_table = 'django_asyncio_task_queue_config'
        ordering = ('label',)
