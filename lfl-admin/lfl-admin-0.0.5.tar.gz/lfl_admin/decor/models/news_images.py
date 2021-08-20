import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.images import Images
from isc_common.models.model_images import Model_imagesManager, Model_imagesQuerySet, Model_images
from lfl_admin.decor.models.news import News

logger = logging.getLogger(__name__)


class News_imagesQuerySet(Model_imagesQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class News_imagesManager(Model_imagesManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return News_imagesQuerySet(self.model, using=self._db)


class News_images(Model_images):
    image = ForeignKeyProtect(Images)
    main_model = ForeignKeyProtect(News)

    objects = News_imagesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('main_model', 'image'),)
