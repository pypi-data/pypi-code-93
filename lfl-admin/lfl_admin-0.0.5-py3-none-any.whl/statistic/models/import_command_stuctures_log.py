import logging

from django.db.models import TextField

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from lfl_admin.statistic.models.import_command_stuctures import Import_command_stuctures

logger = logging.getLogger(__name__)


class Import_command_stuctures_logQuerySet(AuditQuerySet):
    pass


class Import_command_stuctures_logManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'log': record.log,
            'lastmodified': record.lastmodified,
        }
        return res

    def get_queryset(self):
        return Import_command_stuctures_logQuerySet(self.model, using=self._db)


class Import_command_stuctures_log(AuditModel):
    imports = ForeignKeyCascade(Import_command_stuctures)
    log = TextField(db_index=True)
    objects = Import_command_stuctures_logManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Лог импорта составов'
