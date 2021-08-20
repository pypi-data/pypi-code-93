import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager
from isc_common.models.images import Images
from isc_common.models.model_images import Model_imagesQuerySet, Model_images
from lfl_admin.competitions.models.club_logo_history import Club_logo_history

logger = logging.getLogger(__name__)


class Club_logo_history_imagesQuerySet(Model_imagesQuerySet):
    pass


class Club_logo_history_imagesManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Club_logo_history_imagesQuerySet(self.model, using=self._db)


class Club_logo_history_images(Model_images):
    image = ForeignKeyProtect(Images)
    main_model = ForeignKeyProtect(Club_logo_history)

    objects = Club_logo_history_imagesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('image', 'main_model'),)
