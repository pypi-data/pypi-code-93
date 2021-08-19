# coding: utf-8
import inspect
import sys

from django.apps import apps

from django.core.management import BaseCommand
from django.db import models


class Command(BaseCommand):
    help = 'Утилита проверяет, что по всем базовым моделям созданы дочерние'

    def handle(self, **options):
        child_models = apps.get_models()

        success = True

        for name, obj in inspect.getmembers(sys.modules['fias.base_models']):
            if inspect.isclass(obj) and issubclass(obj, models.Model):
                for model in child_models:
                    if issubclass(model, obj):
                        break
                else:
                    self.stdout.write(u"Не найдена модель для {}".format(name))
                    success = False

        if not success:
            sys.exit(u'Найдены не унаследованные базовые модели')