import logging

from bitfield import BitField
from django.db.models import IntegerField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.images import Images
from isc_common.models.model_images import Model_imagesManager, Model_imagesQuerySet, Model_images

from lfl_admin.inventory.models.clothes import Clothes

logger = logging.getLogger(__name__)


class Clothes_imagesQuerySet(Model_imagesQuerySet):
    pass


class Clothes_imagesManager(Model_imagesManager):
    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'Актуальность'),  # 1
        ), default=1, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Clothes_imagesQuerySet(self.model, using=self._db)


class Clothes_images(Model_images, Model_withOldId):
    position = IntegerField()
    image = ForeignKeyProtect(Images)
    main_model = ForeignKeyProtect(Clothes)
    props = Clothes_imagesManager.props()

    objects = Clothes_imagesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('main_model', 'image'),)
