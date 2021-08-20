import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.inventory.models.clothes import Clothes

logger = logging.getLogger(__name__)


class Clubs_clothesQuerySet(AuditQuerySet):
    pass


class Clubs_clothesManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Clubs_clothesQuerySet(self.model, using=self._db)


class Clubs_clothes(AuditModel):
    clothes = ForeignKeyProtect(Clothes)
    club = ForeignKeyProtect(Clubs)

    objects = Clubs_clothesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('clothes', 'club'),)
