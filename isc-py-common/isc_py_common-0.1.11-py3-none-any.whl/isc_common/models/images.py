import logging

from crypto.models.crypto_file import Crypto_file, CryptoManager, CryptoQuerySet
from isc_common import delAttr, delAttr1
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.image_types import Image_types

logger = logging.getLogger(__name__)


class ImagesQuerySet(CryptoQuerySet):

    def create(self, **kwargs):
        if kwargs.get('real_name') is not None:
            try:
                return super().get(real_name=kwargs.get('real_name'))
            except self.model.DoesNotExist:
                return super().create(**kwargs)
        else:
            return super().create(**kwargs)


class ImagesManager(CryptoManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return ImagesQuerySet(self.model, using=self._db)


class Images(Crypto_file):
    image_type = ForeignKeyProtect(Image_types)
    objects = ImagesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Разные картинки '
