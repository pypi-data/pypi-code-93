from django.db import models

class Error(models.Model):
    app_label = models.TextField()
    label = models.TextField()
    task_id = models.TextField()

    exc_type = models.TextField()
    exc_value = models.TextField()
    exc_traceback = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'django_asyncio_task_queue_error'
        ordering = ('-created_at',)
