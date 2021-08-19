from django.db import models


class BaseIoT(models.Model):
    class Meta:
        db_table = 'iot'
        abstract = True

    name = models.CharField(max_length=32, help_text="名称", null=False, unique=True)
    host = models.CharField(max_length=32, help_text="地址", null=False, unique=True)
    username = models.CharField(max_length=32, help_text="用户名")
    password = models.CharField(max_length=32, help_text="密码")
    status = models.BooleanField(default=True)
    addon = models.DateTimeField(auto_now_add=True, help_text="添加时间")
    update = models.DateTimeField(auto_now=True, help_text="最后更新时间")


class IoT(BaseIoT):
    class Meta:
        db_table = 'iot'
        managed = False


class BaseTenant(models.Model):
    class Meta:
        db_table = "tenant"
        abstract = True

    name = models.CharField(null=False, max_length=16, help_text="租户名称", unique=True)
    type = models.CharField(null=False, max_length=16, help_text="租户类型")
    iot = models.ForeignKey(to=IoT, to_field="name", on_delete=models.CASCADE, null=False)
    token = models.CharField(max_length=32, help_text="", null=True, unique=True)
    db = models.CharField(null=True, max_length=16, help_text="数据库")
    es = models.CharField(null=True, max_length=16, help_text="es")
    account = models.CharField(null=False, max_length=16, help_text="账号", unique=True)
    password = models.CharField(null=False, max_length=16, help_text="密码")
    username = models.CharField(null=False, max_length=16, help_text="用户名称", unique=True)
    # creator = models.CharField(max_length=16, help_text="创建人", null=True)
    addon = models.DateTimeField(auto_now_add=True, help_text="添加时间")
    update = models.DateTimeField(auto_now=True, help_text="最后更新时间")


class Tenant(BaseTenant):
    class Meta:
        db_table = "tenant"
        managed = False


class BaseSource(models.Model):
    class Meta:
        db_table = "source"
        abstract = True

    name = models.CharField(max_length=16, null=False, help_text="名称")
    uri = models.CharField(max_length=32, null=False, help_text="uri", unique=True)


class Source(BaseSource):
    class Meta:
        db_table = "source"
        managed = False


class BasePermission(models.Model):
    class Meta:
        db_table = "permission"
        unique_together = ("source", "action")
        abstract = True

    name = models.CharField(max_length=16, null=False, help_text="权限名称", unique=True)

    action = models.CharField(
        max_length=8, choices=(("GET", "GET"), ("POST", "POST"), ("PUT", "PUT"), ("DELETE", "DELETE")), help_text="资源操作"
    )
    source = models.ForeignKey(to=Source, to_field="uri", on_delete=models.SET_NULL, null=True)


class Permission(BasePermission):
    class Meta:
        db_table = "permission"
        unique_together = ("source", "action")
        managed = False


class BaseRole(models.Model):
    class Meta:
        db_table = "role"
        abstract = True

    name = models.CharField(max_length=16, null=False, unique=True, help_text="名称")


class Role(BaseRole):
    class Meta:
        db_table = "role"
        managed = False


class BaseRolePermissions(models.Model):
    class Meta:
        db_table = "role_permissions"
        abstract = True

    role = models.ForeignKey(to=Role, on_delete=models.SET_NULL, to_field="name", null=True)
    permission = models.ForeignKey(to=Permission, to_field="name", on_delete=models.SET_NULL, null=True)


class RolePermissions(BaseRolePermissions):
    class Meta:
        db_table = "role_permissions"
        managed = False


class BaseTenantRole(models.Model):
    class Meta:
        db_table = "tenant_role"
        abstract = True

    tenant = models.ForeignKey(to=Tenant, to_field="account", null=True, on_delete=models.SET_NULL)
    role = models.ForeignKey(to=Role, to_field="name", on_delete=models.SET_NULL, null=True)


class TenantRole(BaseTenantRole):
    class Meta:
        db_table = "tenant_role"
        managed = False
