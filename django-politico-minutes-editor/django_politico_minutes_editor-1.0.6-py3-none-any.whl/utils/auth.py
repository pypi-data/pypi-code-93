from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test

from .importers import import_class


def secure(view):
    """
    Authentication decorator for views.
    If DEBUG is on, we serve the view without authenticating.
    Default is 'django.contrib.auth.decorators.login_required'.
    Can also be 'django.contrib.admin.views.decorators.staff_member_required'
    or a custom decorator.
    """
    auth_decorator = import_class(settings.MINUTES_AUTH_DECORATOR)
    return (
        view
        if settings.DEBUG
        else method_decorator(auth_decorator, name="dispatch")(view)
    )
