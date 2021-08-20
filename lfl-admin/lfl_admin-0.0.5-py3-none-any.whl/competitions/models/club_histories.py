import logging

from bitfield import BitField
from django.db.models import DateField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

from lfl_admin.competitions.models.clubs import Clubs

logger = logging.getLogger(__name__)


class Club_historiesQuerySet(BaseRefQuerySet):
    pass


class Club_historiesManager(BaseRefManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'Актуальность'),  # 1
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
        return Club_historiesQuerySet(self.model, using=self._db)


class Club_histories(BaseRef, Model_withOldId):
    club = ForeignKeyProtect(Clubs)
    end_date = DateField()
    props = Club_historiesManager.props()

    objects = Club_historiesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'История клубов'
