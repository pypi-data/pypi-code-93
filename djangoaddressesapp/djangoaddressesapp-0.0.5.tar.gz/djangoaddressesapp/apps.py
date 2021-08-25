from django.apps import AppConfig
from django.utils.translation import gettext, gettext_lazy as _


class DefaultApp(AppConfig):
    name = 'djangoaddressesapp'
    verbose_name = _('Addresses')
