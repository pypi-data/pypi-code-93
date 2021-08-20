import logging

from bitfield import BitField
from django.db.models import SmallIntegerField

from isc_common.auth.models.user import User
from isc_common.common import undefined
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefManager, BaseRefQuerySet, BaseRef
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class Referee_categoryQuerySet(BaseRefQuerySet):
    pass


class Referee_categoryManager(BaseRefManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'active'),  # 1
        ), default=1, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Referee_categoryQuerySet(self.model, using=self._db)


class Referee_category(BaseRef, Model_withOldId):
    editor = ForeignKeyProtect(User, null=True, blank=True)
    priority = SmallIntegerField()
    props = Referee_categoryManager.props()
    region = ForeignKeyProtect(Regions)

    objects = Referee_categoryManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            code=undefined,
            region=Regions.unknown(),
            priority=0
        )
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Категории судей'
