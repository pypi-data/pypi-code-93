import secrets

from django.db import models
from django.utils import timezone

__all__ = ["JwtAppModel"]


def gen_key() -> str:
    return secrets.token_urlsafe(64)


class JwtAppModel(models.Model):
    """Json Web Token 密钥存储模块"""

    class Meta(object):
        verbose_name = "JWT应用"
        verbose_name_plural = "JWT应用"

    app_name = models.CharField(
        unique=True, max_length=255, verbose_name="密钥名称", help_text="方便人类记忆的名称"
    )

    app_type = models.CharField(
        default="HS256", max_length=32, verbose_name="JWT类型", help_text="密钥的类型"
    )

    app_key = models.TextField(
        default=gen_key,
        unique=True,
        verbose_name="密钥",
        help_text="JWT 加密/解密 使用的密钥",
        editable=False,
    )

    # for ref: https://www.iana.org/assignments/jwt/jwt.xhtml#claims
    jwt_iss = models.CharField(
        max_length=255, verbose_name="JWT ISS", help_text="JSON Web Token iss 字段值"
    )

    ctime = models.DateTimeField(
        default=timezone.now, verbose_name="创建时间", help_text="这个密钥的创建时间", editable=False
    )

    def __str__(self) -> str:
        return f"{self.app_name}"
