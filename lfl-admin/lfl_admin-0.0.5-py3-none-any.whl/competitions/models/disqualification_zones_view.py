import logging

from bitfield import BitField
from django.db.models import SmallIntegerField, BooleanField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldIds
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet
from isc_common.number import DelProps
from lfl_admin.competitions.models.disqualification_zones import Disqualification_zonesManager
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class Disqualification_zones_viewQuerySet(BaseRefQuerySet):
    pass


class Disqualification_zones_viewManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'active': record.active,
            'code': record.code,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'id': record.id,
            'name': record.name,
            'number_of_yellowsold': record.number_of_yellowsold,
            'props': record.props,
            'region__name': record.region.name,
            'region_id': record.region.id,
        }
        return DelProps(res)

    def get_queryset(self):
        return Disqualification_zones_viewQuerySet(self.model, using=self._db)


class Disqualification_viewManager:
    pass


class Disqualification_zones_view(BaseRef, Model_withOldIds):
    active = BooleanField()
    editor = ForeignKeyProtect(User, null=True, blank=True)
    number_of_yellowsold = SmallIntegerField()
    props = Disqualification_zonesManager.props()
    region = ForeignKeyProtect(Regions)

    objects = Disqualification_zones_viewManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            region=Regions.unknown()
        )
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Зоны контроля дисквалификаций'
        db_table = 'competitions_disqualification_zones_view'
        managed = False
