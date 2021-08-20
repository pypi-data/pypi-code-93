import logging

from bitfield import BitField
from django.db.models import SmallIntegerField, CharField

from isc_common.common import undefined
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefHierarcyManager, BaseRefHierarcyQuerySet, BaseRef
from lfl_admin.competitions.models.seasons import Seasons
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class LeaguesQuerySet(BaseRefHierarcyQuerySet):
    pass


class LeaguesManager(BaseRefHierarcyManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'active'),  # 1
            ('parimatch', 'parimatch'),  # 1
            ('submenu', 'submenu'),  # 1
            ('nonphoto', 'nonphoto'),  # 1
            ('show_in_menu', 'show_in_menu'),  # 1
            ('show_referee_photo_in_protocols', 'show_referee_photo_in_protocols'),  # 1
            ('show_stadium_photo_in_protocols', 'show_stadium_photo_in_protocols'),  # 1
            ('show_shirt_in_protocols', 'show_shirt_in_protocols'),  # 1
        ), default=1, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return BaseRefHierarcyQuerySet(self.model, using=self._db)


class Leagues(BaseRef, Model_withOldId):
    add_slideshow_tabs = CharField(max_length=255, null=True, blank=True)
    code = CodeField()
    position = SmallIntegerField(default=1)
    referees_max = SmallIntegerField(default=1)
    region = ForeignKeyProtect(Regions)
    season = ForeignKeyProtect(Seasons)
    slideshow_title = CharField(max_length=255, null=True, blank=True)

    props = LeaguesManager.props()

    objects = LeaguesManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            code=undefined,
            defaults=dict(
                season=Seasons.unknown(),
                region=Regions.unknown()
            ))
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Лиги'
