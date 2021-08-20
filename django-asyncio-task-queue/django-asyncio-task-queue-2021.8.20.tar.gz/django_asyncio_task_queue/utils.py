from datetime import datetime

from django.apps import apps

from .models import AbstractTask, Error, Log, Stat

def get_models():
    return list(filter(
        lambda m:issubclass(m,AbstractTask) and not m._meta.abstract,
        apps.get_models()
    ))
