import logging

from bitfield import BitField
from django.conf import settings
from django.db.models import BooleanField, TextField

from isc_common.common import undefined
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefQuerySet, BaseRefManager
from isc_common.models.standard_colors import Standard_colors
from isc_common.number import DelProps
from lfl_admin.competitions.models.seasons import Seasons
from lfl_admin.region.models.region_zones import Region_zones
from lfl_admin.region.models.regions import RegionsManager

logger = logging.getLogger(__name__)


class Regions_viewQuerySet(BaseRefQuerySet):
    pass


class Regions_viewManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'active': record.active,
            'code': record.code,
            'color__color': record.color.color if record.color else None,
            'color__name': record.color.name if record.color else None,
            'color_id': record.color.id if record.color else None,
            'deliting': record.deliting,
            'description': record.description,
            'contacts': record.contacts,
            'editing': record.editing,
            'id': record.id,
            'logo_real_name': record.logo_real_name,
            'logo_src': f'http://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.logo_image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}',
            'header_real_name': record.header_real_name,
            'header_src': f'http://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.header_image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}',
            'name': record.name,
            'parent': record.parent.id if record.parent else None,
            'season__name': record.season.name,
            'season_id': record.season.id,
            'zone__name': record.zone.name if record.zone else None,
            'zone_id': record.zone.id if record.zone else None,
        }
        return DelProps(res)

    def get_queryset(self):
        return Regions_viewQuerySet(self.model, using=self._db)


class Regions_view(BaseRefHierarcy, Model_withOldId):
    active = BooleanField()
    color = ForeignKeyProtect(Standard_colors, null=True, blank=True)
    contacts = TextField(null=True, blank=True)
    logo_image_src = NameField()
    logo_real_name = NameField()
    header_image_src = NameField()
    header_real_name = NameField()
    props = RegionsManager.props()
    season = ForeignKeyProtect(Seasons)
    zone = ForeignKeyProtect(Region_zones, null=True, blank=True)

    objects = Regions_viewManager()

    def __str__(self):
        return f'ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}, color: [{self.color}], season: [{self.season}], zone: [{self.zone}], props: [{self.props}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Регионы'
        db_table = 'region_region_view'
        managed = False
