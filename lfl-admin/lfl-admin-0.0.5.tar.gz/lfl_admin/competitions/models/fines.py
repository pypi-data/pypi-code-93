import logging

from bitfield import BitField
from django.db.models import DateField, IntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldId
from isc_common.models.audit_ex import AuditModelEx
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.decor.models.news import News

logger = logging.getLogger(__name__)


class FinesQuerySet(AuditQuerySet):
    pass


class FinesManager(AuditManager):
    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'active'),  # 1
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
        return FinesQuerySet(self.model, using=self._db)


class Fines(AuditModelEx, Model_withOldId):
    club = ForeignKeyProtect(Clubs)
    date = DateField(null=True, blank=True)
    kdk = ForeignKeyProtect(News)
    payment = IntegerField()
    props = FinesManager.props()
    remove_restore_date = DateField(null=True, blank=True)
    sum = IntegerField()

    objects = FinesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Реестр штрафов'
