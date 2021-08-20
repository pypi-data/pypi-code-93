import logging

from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditModel
from isc_common.models.text_informations import Model_text_informationsQuerySet, Text_informations
from lfl_admin.competitions.models.players import Players

logger = logging.getLogger(__name__)


class Players_text_informationsQuerySet(Model_text_informationsQuerySet):
    pass


class Players_text_informationsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Players_text_informationsQuerySet(self.model, using=self._db)


class Players_text_informations(AuditModel):
    code = CodeStrictField()
    text = ForeignKeyProtect(Text_informations)
    player = ForeignKeyProtect(Players)

    objects = Players_text_informationsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
