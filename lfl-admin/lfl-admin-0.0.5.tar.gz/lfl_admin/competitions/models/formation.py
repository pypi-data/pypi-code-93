import logging

from bitfield import BitField
from django.db.models import SmallIntegerField

from isc_common.auth.models.user import User
from isc_common.common import undefined
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class FormationQuerySet(BaseRefQuerySet):
    pass


class FormationManager(BaseRefManager):

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
        return FormationQuerySet(self.model, using=self._db)


class Formation(BaseRef, Model_withOldId):
    priority = SmallIntegerField(null=True, blank=True)
    number_of_players = SmallIntegerField()
    editor = ForeignKeyProtect(User, null=True, blank=True)
    props = FormationManager.props()

    objects = FormationManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            code=undefined,
            number_of_players=0
        )
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Расстановки игроков в сыгранных матчах'
