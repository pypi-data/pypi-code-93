from __future__ import annotations

import typing

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from ob_dj_otp.core.users.managers import UserManager


class User(AbstractUser):
    class LANGUAGES(models.TextChoices):
        EN = "en", _("English")
        AR = "ar", _("Arabic")

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[AbstractUser.username_validator],
        error_messages={"unique": _("A user with that username already exists."),},
    )

    email = models.EmailField(_("email address"), unique=True, blank=False, null=False)
    is_email_verified = models.BooleanField(default=False)
    phone_number = PhoneNumberField(
        unique=True,
        error_messages={"unique": _("A user with that phone number already exists."),},
    )

    language = models.CharField(
        _("Language"), choices=LANGUAGES.choices, default=LANGUAGES.EN, max_length=5
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS: typing.List[typing.Any] = []

    class Meta:
        verbose_name_plural = _("Users")

    @property
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> typing.Text:
        return f"{self.email}"

    def __unicode__(self) -> typing.Text:
        return self.__str__()

    def full_clean(
        self,
        exclude: typing.Optional[typing.Collection[str]] = None,
        validate_unique: bool = True,
    ) -> None:
        exclude = exclude or ("email", "password")
        super().full_clean(exclude=exclude, validate_unique=validate_unique)
