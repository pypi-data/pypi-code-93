import logging

from django.db.models import SmallIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId, AuditModel
from isc_common.models.base_ref import BaseRefQuerySet, BaseRefManager, BaseRef
from lfl_admin.competitions.models.calendar import Calendar

logger = logging.getLogger(__name__)


class Match_resaultsQuerySet(BaseRefQuerySet):
    pass


class Match_resaultsManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Match_resaultsQuerySet(self.model, using=self._db)


class Match_resaults(AuditModel, Model_withOldId):
    away_score = SmallIntegerField(null=True, blank=True)
    home_score = SmallIntegerField(null=True, blank=True)
    match = ForeignKeyProtect(Calendar)
    user = ForeignKeyProtect(User)

    objects = Match_resaultsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Раунды кубкового турнира'
