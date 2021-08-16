import secrets
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

__all__ = ["BearerTokenModel"]


def gen_token() -> str:
    return secrets.token_urlsafe(64)


class BearerTokenModel(models.Model):
    """Bearer 令牌存储模块"""

    class Meta(object):
        verbose_name = "Bearer令牌"
        verbose_name_plural = "Bearer令牌"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name="用户",
        help_text="拥有这个令牌的用户",
    )

    token_name = models.CharField(
        max_length=255, verbose_name="令牌名称", help_text="方便人类记忆的名称"
    )

    token_type = models.CharField(
        default="default", max_length=255, verbose_name="令牌类型", help_text="访问令牌的类型"
    )

    token_value = models.CharField(
        default=gen_token,
        max_length=255,
        unique=True,
        verbose_name="访问令牌",
        editable=False,
    )

    revoked = models.BooleanField(
        default=False, verbose_name="已撤销", help_text="这个访问令牌是否已经撤销"
    )

    expire_time = models.DateTimeField(
        db_index=True, verbose_name="过期时间", help_text="这个令牌的失效时间"
    )

    create_time = models.DateTimeField(
        default=timezone.now, verbose_name="创建时间", help_text="这个令牌的创建时间", editable=False
    )

    def __str__(self) -> str:
        return f"{self.token_name}({self.user}:{self.expire_time})"

    def revoke_token(self):
        """撤销令牌"""
        self.revoked = True
        self.save()

    @property
    def is_valid(self) -> bool:
        """检测 访问令牌是否有效"""
        if self.revoked:
            return False
        if self.expire_time < timezone.now():
            return False
        return True

    @staticmethod
    def check_token(token_value: str) -> "BearerTokenModel":
        """
        检测 token 是否有效
        如果 token_value 不存在 抛出 ObjectDoesNotExists 异常
        """
        return BearerTokenModel.objects.get(token_value=token_value)

    @staticmethod
    def create_token(
        user: User, token_name: str, duration: timedelta, token_type: str = "default"
    ):
        return BearerTokenModel.objects.create(
            user=user,
            token_name=token_name,
            token_type=token_type,
            expire_time=timezone.now() + duration,
        )

    @staticmethod
    def purge_expire_token():
        """删除所有已经过期的令牌"""
        BearerTokenModel.objects.filter(expire_time__lt=timezone.now()).delete()

    @staticmethod
    def purge_revoked_token():
        """删除已经撤销授权的令牌"""
        BearerTokenModel.objects.filter(revoked=True).delete()

    @staticmethod
    def purge_invalid_token():
        """删除所有无效的令牌"""
        BearerTokenModel.purge_expire_token()
        BearerTokenModel.purge_revoked_token()
