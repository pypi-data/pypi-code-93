from django.test.utils import TestContextDecorator

from dj_dynamic_settings.conf import settings


class OverrideSettings(TestContextDecorator):
    def __init__(self, **kwargs):
        self.options = kwargs
        super(OverrideSettings, self).__init__()
        self.previous = None

    def enable(self):
        self.previous = settings.holder
        new_holder = dict(**self.previous) if self.previous else {}
        new_holder.update(**self.options)
        settings.holder = new_holder

    def disable(self):
        settings.holder = self.previous
        self.previous = None


override_settings = OverrideSettings
