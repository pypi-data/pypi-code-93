import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager
from isc_common.models.images import Images
from isc_common.models.model_images import Model_imagesQuerySet, Model_images
from lfl_admin.competitions.models.clubs import Clubs

logger = logging.getLogger(__name__)


class Clubs_imagesQuerySet(Model_imagesQuerySet):
    pass


class Clubs_imagesManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Clubs_imagesQuerySet(self.model, using=self._db)


class Clubs_images(Model_images):
    image = ForeignKeyProtect(Images)
    main_model = ForeignKeyProtect(Clubs)

    objects = Clubs_imagesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('image', 'main_model'),)
