import logging

from django.conf import settings

from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet, BaseRefHierarcy

from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class Cities_viewQuerySet(BaseRefQuerySet):
    pass


class Cities_viewManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'code': record.code,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'id': record.id,
            'logo_real_name': record.real_name,
            'logo_src': f'http://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}',
            'name': record.name,
            'region__name': record.region.name if record.region is not None else None,
            'region_id': record.region.id if record.region is not None else None,
        }
        return res

    def get_queryset(self):
        return Cities_viewQuerySet(self.model, using=self._db)


class Cities_view(BaseRef, Model_withOldId):
    region = ForeignKeyProtect(Regions, null=True, blank=True)

    image_src = NameField()
    real_name = NameField()

    objects = Cities_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Города'
        db_table = 'region_cities_view'
        managed = False
