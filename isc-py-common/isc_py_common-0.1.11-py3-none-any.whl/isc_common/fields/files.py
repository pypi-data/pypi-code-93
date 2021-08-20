import os

from django.conf import settings
from django.db.models import FileField
from django.db.models.fields.files import FieldFile

from isc_common.fields import Field


class FieldFileEx(FieldFile, Field):
    def get_replaced_name(self):
        if isinstance(settings.REPLACE_FILE_PATH, dict):
            for key, value in settings.REPLACE_FILE_PATH.items():
                self.name = self.name.replace(key, value)
        return self.name

    def open(self, mode='rb'):
        self._require_file()
        if isinstance(settings.REPLACE_FILE_PATH, dict):
            for key, value in settings.REPLACE_FILE_PATH.items():
                    self.name = self.name.replace(key, value)
        self.file = self.storage.open(self.name, mode)
        return self

    def save(self, name, content, save=True):
        name = os.path.abspath(name)
        self.name = self.storage.save(name, content, max_length=self.field.max_length)
        setattr(self.instance, self.field.name, self.name)

        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()


class FileFieldEx(FileField):
    attr_class = FieldFileEx
