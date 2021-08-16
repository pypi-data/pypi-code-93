import jwt
from django.db import models
from django.utils import timezone

from .jwt_app import JwtAppModel

__all__ = ["JwtTokenModel"]


class JwtTokenModel(models.Model):
    """Json Web Token 令牌存储模块"""

    class Meta(object):
        verbose_name = "JWT令牌"
        verbose_name_plural = "JWT令牌"

    jwt_app = models.ForeignKey(
        JwtAppModel,
        on_delete=models.CASCADE,
        verbose_name="JWT应用",
        help_text="JSON web token 应用",
    )

    jwt_sub = models.CharField(
        max_length=255, verbose_name="JWT sub", help_text="JSON web token sub 用户字段的值"
    )

    jwt_aud = models.CharField(
        max_length=255, verbose_name="JWT aud", help_text="JSON web token aud 目标用户字段"
    )

    jwt_exp = models.DateTimeField(
        verbose_name="JWT exp", help_text="JSON web token exp 过期时间字段"
    )

    jwt_nbf = models.DateTimeField(
        default=timezone.now,
        verbose_name="JWT nbf",
        help_text="JSON web token nbf 不早于时间时间字段",
    )

    def __str__(self) -> str:
        return f"{self.jwt_sub}({self.jwt_app})"

    @property
    def jwt_token(self) -> str:
        return jwt.encode(
            {
                "iss": self.jwt_app.jwt_iss,
                "sub": self.jwt_sub,
                "aud": self.jwt_aud,
                "exp": self.jwt_exp,
                "nbf": self.jwt_nbf,
            },
            self.jwt_app.app_key,
            algorithm=self.jwt_app.app_type,
        )
