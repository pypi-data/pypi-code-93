from django.db import models


class BaseModels(models.Model):
    class Meta:
        abstract = True

    creator = models.CharField(max_length=16, help_text="创建人", null=True)
    addon = models.DateTimeField(auto_now_add=True, help_text="添加时间", editable=True)
    update = models.DateTimeField(auto_now=True, help_text="最后更新时间", editable=True)
