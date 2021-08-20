import logging

from bitfield import BitField
from django.db.models import SmallIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.images import Images
from isc_common.models.links import Links
from isc_common.models.model_images import Model_imagesManager, Model_imagesQuerySet, Model_images
from isc_common.views.model_links import Model_links
from lfl_admin.decor.models.banners_type import Banners_type
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class BannersQuerySet(Model_imagesQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class BannersManager(Model_imagesManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'active'),  # 1
            ('overlap', 'overlap'),  # 1
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
        return BannersQuerySet(self.model, using=self._db)


class Banners(Model_images, Model_links, Model_withOldId):
    banner_type = ForeignKeyProtect(Banners_type)
    href = ForeignKeyProtect(Links, null=True, blank=True)
    image = ForeignKeyProtect(Images, null=True, blank=True)
    padding_top = SmallIntegerField(null=True, blank=True)
    position = SmallIntegerField()
    props = BannersManager.props()
    region = ForeignKeyProtect(Regions, null=True, blank=True)
    rotate = SmallIntegerField(null=True, blank=True)

    objects = BannersManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Банеры'
