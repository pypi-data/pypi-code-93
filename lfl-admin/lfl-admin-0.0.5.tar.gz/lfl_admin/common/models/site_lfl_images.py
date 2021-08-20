import logging
import os

from django.conf import settings
from django.db.models import TextField, CharField, FloatField

from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel

logger = logging.getLogger(__name__)


class Site_lfl_imagesImagesQuerySet(AuditQuerySet):
    pass


class Site_lfl_imagesManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Site_lfl_imagesImagesQuerySet(self.model, using=self._db)


class Site_lfl_images(AuditModel):
    path = TextField(db_index=True, unique=True)
    date = FloatField()
    file_name = CharField(max_length=255, db_index=True)

    objects = Site_lfl_imagesManager()

    @classmethod
    def get_image(cls, file_name, path=None):
        if file_name is None:
            return None

        if os.altsep is None:
            os.altsep = '\\'

        have_path = file_name.find(os.altsep) != -1
        if have_path is False:
            have_path = file_name.find(os.sep) != -1

        if have_path:
            if os.altsep is None:
                file_name1 = f'{settings.OLD_SITE_BASE_DIR}{file_name}'.replace(os.sep, '\\')
            else:
                file_name1 = f'{settings.OLD_SITE_BASE_DIR}{file_name}'.replace(os.altsep, os.sep)
            try:
                return cls.objects.get(path__upper=file_name1.upper()).path
            except cls.DoesNotExist:
                return None

        query = cls.objects.filter(file_name=file_name).order_by('-date')
        if query.count() == 0:
            return None
        else:
            _list = list(map(lambda x: x.path, query))
            if path is None:
                return _list[0]

            for item in _list:
                if item.find(path) != -1:
                    return item
            return None

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Старые изображения'
