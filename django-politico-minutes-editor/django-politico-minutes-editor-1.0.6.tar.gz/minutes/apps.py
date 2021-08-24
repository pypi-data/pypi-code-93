from django.apps import AppConfig


class MinutesConfig(AppConfig):
    name = "minutes"

    def ready(self):
        from minutes import signals  # noqa
