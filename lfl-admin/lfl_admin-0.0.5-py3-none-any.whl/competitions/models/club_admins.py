import logging

from bitfield import BitField
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet, Model_withOldId

from lfl_admin.competitions.models.clubs import Clubs

logger = logging.getLogger(__name__)


class Club_adminsQuerySet(AuditQuerySet):
    pass


class Club_adminsManager(AuditManager):
    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'Актуальность'),  # 1
        ), default=1, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Club_adminsQuerySet(self.model, using=self._db)


class Club_admins(AuditModel, Model_withOldId):
    club = ForeignKeyProtect(Clubs)
    user = ForeignKeyProtect(User)
    props = Club_adminsManager.props()

    objects = Club_adminsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Администрация клуба'
        unique_together = (('user', 'club', 'props'),)
