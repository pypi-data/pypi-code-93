import logging

from bitfield import BitField

from isc_common.common import undefined
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefQuerySet, BaseRefManager
from isc_common.models.standard_colors import Standard_colors
from lfl_admin.competitions.models.seasons import Seasons
from lfl_admin.region.models.region_zones import Region_zones

logger = logging.getLogger(__name__)


class RegionsQuerySet(BaseRefQuerySet):
    pass


class RegionsManager(BaseRefManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'Актуальность'),  # 1
            ('select_division', 'select_division'),  # 2
            ('parimatch', 'parimatch'),  # 4
            ('submenu', 'submenu'),  # 8
            ('leagues_menu', 'leagues_menu'),  # 16
        ), default=1, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'code': record.code,
            'color__color': record.color.color if record.color else None,
            'color__name': record.color.name if record.color else None,
            'color_id': record.color.id if record.color else None,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'id': record.id,
            'name': record.name,
            'parent': record.parent.id if record.parent else None,
            'season__name': record.season.name,
            'season_id': record.season.id,
            'zone__name': record.zone.name if record.zone else None,
            'zone_id': record.zone.id if record.zone else None,
        }
        return res

    def get_queryset(self):
        return RegionsQuerySet(self.model, using=self._db)


class Regions(BaseRefHierarcy, Model_withOldId):
    color = ForeignKeyProtect(Standard_colors, null=True, blank=True)
    props = RegionsManager.props()
    season = ForeignKeyProtect(Seasons)
    zone = ForeignKeyProtect(Region_zones, null=True, blank=True)

    objects = RegionsManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            code=undefined,
            defaults=dict(
                name='Неопределенный',
                season=Seasons.unknown(),
                zone=Region_zones.unknown()
            ))
        return res

    def __str__(self):
        return f'ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}, color: [{self.color}], season: [{self.season}], zone: [{self.zone}], props: [{self.props}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Регионы'
