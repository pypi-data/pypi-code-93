import logging

from django.db.models import DateField, SmallIntegerField, BooleanField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldIds
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefHierarcyManager, BaseRefHierarcyQuerySet
from lfl_admin.competitions.models.clubs import ClubsManager
from lfl_admin.competitions.models.leagues import Leagues
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class Clubs_viewQuerySet(BaseRefHierarcyQuerySet):
    pass


class Clubs_viewManager(BaseRefHierarcyManager):

    @staticmethod
    def getRecord(record):
        res = {
            'active': record.active,
            'code': record.code,
            'created_date': record.created_date,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'id': record.id,
            'interregion': record.interregion,
            'league__name': record.league.name,
            'league_id': record.league.id,
            'name': record.name,
            'parent': record.parent.id if record.parent else None,
            'region__name': record.region.name,
            'region_id': record.region.id,
        }
        return res

    def get_queryset(self):
        return BaseRefHierarcyQuerySet(self.model, using=self._db)


class Clubs_view(BaseRefHierarcy, Model_withOldIds):
    active = BooleanField()
    created_date = DateField(null=True, blank=True)
    editor = ForeignKeyProtect(User, related_name='Clubs_view_editor', null=True, blank=True)
    interregion = SmallIntegerField(null=True, blank=True)
    league = ForeignKeyProtect(Leagues)
    region = ForeignKeyProtect(Regions)

    props = ClubsManager.props()

    objects = Clubs_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Клубы'
        db_table = 'competitions_clubs_view'
        managed = False
