import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.images import Images
from isc_common.models.model_images import Model_imagesManager, Model_imagesQuerySet, Model_images
from lfl_admin.region.models.cities import Cities

logger = logging.getLogger(__name__)


class City_imagesQuerySet(Model_imagesQuerySet):
    pass


class City_imagesManager(Model_imagesManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return City_imagesQuerySet(self.model, using=self._db)


class City_images(Model_images):
    image = ForeignKeyProtect(Images)
    main_model = ForeignKeyProtect(Cities)

    objects = City_imagesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('main_model', 'image'),)
