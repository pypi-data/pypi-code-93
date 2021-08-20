import logging

from django.db.models import DateTimeField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from lfl_admin.competitions.models.clubs import Clubs

logger = logging.getLogger(__name__)


class Club_logo_historyQuerySet(AuditQuerySet):
    pass


class Club_logo_historyManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Club_logo_historyQuerySet(self.model, using=self._db)


class Club_logo_history(AuditModel):
    code = CodeStrictField()
    club = ForeignKeyProtect(Clubs)
    dt = DateTimeField()
    admin = ForeignKeyProtect(User)

    objects = Club_logo_historyManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'История логотипов клуба'
