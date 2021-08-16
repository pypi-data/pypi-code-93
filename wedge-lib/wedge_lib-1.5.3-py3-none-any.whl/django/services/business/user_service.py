from django.contrib.auth.models import User
from django.db import models
from w.services.abstract_model_service import AbstractModelService
from w import exceptions


class UserService(AbstractModelService):
    _model = User

    @classmethod
    def get_or_create(cls, **attrs):
        # noinspection PyUnresolvedReferences
        try:
            return cls._model.objects.get(username=attrs.get("username"))
        except cls._model.DoesNotExist:
            return cls._model.objects.create(**attrs)

    @classmethod
    def create(cls, **attrs) -> models.Model:
        return User.objects.create_user(**attrs)

    @classmethod
    def get_by_email(cls, email):
        """
        Retrieve user by its email

        Returns:
            User
        """
        return cls._model.objects.get(email=email)

    @classmethod
    def check_by_email(cls, email):
        """
        Check user exists by its email

        if found return user else raise NotFoundError

        Raises
            NotFoundError
        """
        # noinspection PyUnresolvedReferences
        try:
            return cls.get_by_email(email)
        except cls._model.DoesNotExist:
            raise exceptions.NotFoundError(f"user not found (email={email})")
