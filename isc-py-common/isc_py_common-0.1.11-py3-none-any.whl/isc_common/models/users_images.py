import logging

from bitfield import BitField
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldIds
from isc_common.models.images import Images
from isc_common.models.model_images import Model_imagesQuerySet, Model_images, Model_imagesManager

logger = logging.getLogger(__name__)


class Users_imagesQuerySet(Model_imagesQuerySet):
    pass


class Users_imagesManager(Model_imagesManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('main_photo', 'main_photo'),  # 1
        ), default=0, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Users_imagesQuerySet(self.model, using=self._db)


class Users_images(Model_images, Model_withOldIds):
    image = ForeignKeyProtect(Images)
    main_model = ForeignKeyProtect(User)
    props = Users_imagesManager.props()

    objects = Users_imagesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('image', 'main_model', 'props'),)
