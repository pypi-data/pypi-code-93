from django.db import models

class Log(models.Model):
    app_label = models.TextField()
    label = models.TextField()
    task_id = models.TextField()

    msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'django_asyncio_task_queue_log'
        ordering = ('-created_at',)
