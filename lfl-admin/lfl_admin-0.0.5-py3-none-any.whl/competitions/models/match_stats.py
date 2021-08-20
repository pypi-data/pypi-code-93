import logging

from django.db.models import SmallIntegerField, CharField

from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId, AuditModel
from isc_common.models.base_ref import BaseRefQuerySet, BaseRefManager, BaseRef
from lfl_admin.competitions.models.calendar import Calendar

logger = logging.getLogger(__name__)


class Match_statsQuerySet(BaseRefQuerySet):
    pass


class Match_statsManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Match_statsQuerySet(self.model, using=self._db)


class Match_stats(AuditModel, Model_withOldId):
    away_value = SmallIntegerField(null=True, blank=True)
    home_value = SmallIntegerField(null=True, blank=True)
    stat_key = CodeField()
    stat_title = NameField()
    match = ForeignKeyProtect(Calendar)

    objects = Match_statsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Раунды кубкового турнира'
