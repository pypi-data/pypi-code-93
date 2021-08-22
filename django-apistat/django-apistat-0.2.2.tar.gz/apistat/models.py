from django.conf import settings
from django.db import models


class ApiStatSpr(models.Model):
    shortName = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    sql = models.TextField()
    db_alias = models.CharField(max_length=50, blank = True)

