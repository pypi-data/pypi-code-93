import logging

from django.db.models import OneToOneField, PROTECT

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class Users_regionsQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Users_regionsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Users_regionsQuerySet(self.model, using=self._db)


class Users_regions(AuditModel):
    region = ForeignKeyProtect(Regions)
    user = OneToOneField(User, on_delete=PROTECT)

    objects = Users_regionsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('region', 'user'),)
