from django.db import models

class Message(models.Model):
    app = models.TextField()
    name = models.TextField()
    pid = models.IntegerField()
    msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'django_command_debug_message'
        indexes = [
           models.Index(fields=['app',]),
           models.Index(fields=['name',]),
           models.Index(fields=['-created_at',]),
        ]
        ordering = ('-created_at',)
