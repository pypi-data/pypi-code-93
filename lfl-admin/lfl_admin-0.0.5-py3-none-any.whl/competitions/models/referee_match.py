import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from lfl_admin.competitions.models.calendar import Calendar
from lfl_admin.competitions.models.referees import Referees

logger = logging.getLogger(__name__)


class Referee_matchQuerySet(AuditQuerySet):
    pass


class Referee_matchManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Referee_matchQuerySet(self.model, using=self._db)


class Referee_match(AuditModel):
    match = ForeignKeyProtect(Calendar)
    referee = ForeignKeyProtect(Referees)

    objects = Referee_matchManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Главные судьи в матчах'
