import logging

from django.conf import settings
from django.db.models import BooleanField, TextField

from isc_common.fields.name_field import NameField
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefHierarcyManager, BaseRefHierarcyQuerySet, BaseRefHierarcy
from isc_common.number import DelProps
from lfl_admin.region.models.region_zones import Region_zonesManager

logger = logging.getLogger(__name__)


class Region_zones_viewQuerySet(BaseRefHierarcyQuerySet):
    pass


class Region_zones_viewManager(BaseRefHierarcyManager):

    @staticmethod
    def getRecord(record):
        res = {
            'blocked': record.blocked,
            'code': record.code,
            'contacts': record.contacts,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'id': record.id,
            'logo_real_name': record.logo_real_name,
            'logo_src': f'http://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.logo_image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}',
            'name': record.name,
            'parent': record.parent.id if record.parent else None,
            'props': record.props,
            'text': record.text,
        }
        return DelProps(res)

    def get_queryset(self):
        return Region_zones_viewQuerySet(self.model, using=self._db)


class Region_zones_view(BaseRefHierarcy, Model_withOldId):
    blocked = BooleanField()
    logo_image_src = NameField()
    logo_real_name = NameField()
    text = TextField(null=True, blank=True)
    contacts = TextField(null=True, blank=True)
    props = Region_zonesManager.props()
    objects = Region_zones_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Зоны регионов'
        db_table = 'region_region_zones_view'
        managed = False
