from django.db import models
from tenant_auth.models import Tenant


class BaseModels(models.Model):
    class Meta:
        abstract = True

    creator = models.ForeignKey(to=Tenant, to_field="name", on_delete=models.SET_DEFAULT, default='admin')
    addon = models.DateTimeField(auto_now_add=True, help_text="添加时间", editable=True)
    update = models.DateTimeField(auto_now=True, help_text="最后更新时间", editable=True)
