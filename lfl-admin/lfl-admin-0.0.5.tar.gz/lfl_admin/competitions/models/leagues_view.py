import logging

from django.conf import settings
from django.db.models import SmallIntegerField, CharField, TextField, BooleanField

from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefHierarcyManager, BaseRefHierarcyQuerySet, BaseRef
from isc_common.number import DelProps
from lfl_admin.competitions.models.leagues import LeaguesManager
from lfl_admin.competitions.models.seasons import Seasons
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class Leagues_viewQuerySet(BaseRefHierarcyQuerySet):
    pass


class Leagues_viewManager(BaseRefHierarcyManager):

    @staticmethod
    def getRecord(record):
        res = {
            'active': record.active,
            'code': record.code,
            'contacts': record.contacts,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'header_real_name': record.header_real_name,
            'header_src': f'http://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.header_image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}',
            'id': record.id,
            'logo_real_name': record.logo_real_name,
            'logo_src': f'http://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.logo_image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}',
            'name': record.name,
            'props': record.season.props,
            'season__name': record.season.name,
            'season_id': record.season.id,
        }
        return DelProps(res)

    def get_queryset(self):
        return BaseRefHierarcyQuerySet(self.model, using=self._db)


class Leagues_view(BaseRef, Model_withOldId):
    active = BooleanField()
    add_slideshow_tabs = CharField(max_length=255, null=True, blank=True)
    code = CodeField()
    contacts = TextField(null=True, blank=True)
    header_image_src = NameField()
    header_real_name = NameField()
    logo_image_src = NameField()
    logo_real_name = NameField()
    position = SmallIntegerField(default=1)
    referees_max = SmallIntegerField(default=1)
    region = ForeignKeyProtect(Regions)
    season = ForeignKeyProtect(Seasons)
    slideshow_title = CharField(max_length=255, null=True, blank=True)

    props = LeaguesManager.props()

    objects = Leagues_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Лиги'
        db_table = 'competitions_leagues_view'
        managed = False
