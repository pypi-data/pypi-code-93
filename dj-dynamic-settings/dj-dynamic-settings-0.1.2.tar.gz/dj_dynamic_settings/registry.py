from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import RegexValidator

setting_key_regex = r"^[A-Z]{1}[A-Z0-9_]*$"
setting_key_validator = RegexValidator(regex=setting_key_regex)


class Unset(object):
    pass


class BaseSetting(object):
    key = None
    validators = []
    default = Unset
    description = None


class SettingsRegistry(object):
    def __init__(self):
        self._registry = {}

    def register(self, setting_cls):
        if setting_cls.key in self._registry:
            raise ValueError("%s already registered." % setting_cls.key)

        try:
            setting_key_validator(setting_cls.key)
        except ValidationError:
            raise ImproperlyConfigured(
                "'%s' does not match regex '%s'." % (setting_cls.key, setting_key_regex)
            )

        self._registry[setting_cls.key] = setting_cls

    def keys(self):
        return self._registry.keys()

    def __getitem__(self, item):
        return self._registry[item]

    def __contains__(self, item):
        return self._registry.__contains__(item)


registry = SettingsRegistry()
