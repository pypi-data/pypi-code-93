import logging
import os

from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)


def getenv_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() == "true"


def create_superuser(sender, **kwargs):
    user_model = get_user_model()

    def is_user(user):
        return user_model.objects.filter(username=user).exists()

    create = getenv_bool("DJANGO_SUPERUSER_CREATE")

    if create:
        logger.info("Creating new superuser.")

        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not username:
            logger.warning(
                "Username not provided. Please populate the DJANGO_SUPERUSER_USERNAME environment variable. Exiting."
            )
            return

        if not email:
            logger.warning(
                "Email not provided. Please populate the DJANGO_SUPERUSER_EMAIL environment variable. Exiting."
            )
            return

        if not password:
            logger.warning(
                "Password not provided. Please populate the DJANGO_SUPERUSER_PASSWORD environment variable. Exiting."
            )
            return

        if is_user(username):
            logger.info("User %s already exists.", username)
            return

        user_model.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
