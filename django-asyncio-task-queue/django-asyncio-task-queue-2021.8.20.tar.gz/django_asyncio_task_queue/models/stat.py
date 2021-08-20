from django.db import models

class Stat(models.Model):
    app_label = models.CharField(max_length=255)
    label = models.CharField(max_length=255,unique=True)
    error_count = models.IntegerField(null=True,verbose_name='errors')
    log_count = models.IntegerField(null=True,verbose_name='logs')

    updated_at = models.DateTimeField(null=True,verbose_name='updated')

    class Meta:
        db_table = 'django_asyncio_task_queue_stat'
        ordering = ('label',)
