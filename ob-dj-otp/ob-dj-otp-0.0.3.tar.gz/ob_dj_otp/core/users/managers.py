import uuid

from django.contrib.auth.models import UserManager as BaseUserManager


class UserManager(BaseUserManager):
    def create_superuser(self, email, password, **extra_fields):
        username = uuid.uuid4().__str__()
        return super(UserManager, self).create_superuser(
            username=username, email=email, password=password, **extra_fields
        )

    def create_user(self, email=None, password=None, **extra_fields):
        if not "username" in extra_fields.keys():
            extra_fields["username"] = uuid.uuid4().__str__()
        return super(UserManager, self).create_user(
            email=email, password=password, **extra_fields
        )
