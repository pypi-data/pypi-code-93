import logging

from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager
from isc_common.models.links import Model_linksQuerySet, Links
from lfl_admin.competitions.models.calendar import Calendar

logger = logging.getLogger(__name__)


class Calendar_linksQuerySet(Model_linksQuerySet):
    pass


class Calendar_linksManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Calendar_linksQuerySet(self.model, using=self._db)


class Calendar_links(AuditModel):
    code = CodeStrictField()
    link = ForeignKeyProtect(Links)
    calendar = ForeignKeyProtect(Calendar)

    objects = Calendar_linksManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('link', 'calendar', 'code'),)
