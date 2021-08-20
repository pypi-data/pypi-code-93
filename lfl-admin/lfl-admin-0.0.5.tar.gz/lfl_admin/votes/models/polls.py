import logging

from bitfield import BitField
from django.db.models import SmallIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.base_ref import BaseRefQuerySet, BaseRefManager, BaseRef

logger = logging.getLogger(__name__)


class PollsQuerySet(BaseRefQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class PollsManager(BaseRefManager):

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
        return PollsQuerySet(self.model, using=self._db)


class Polls(BaseRef):
    editor = ForeignKeyProtect(User, null=True, blank=True)
    min_answers = SmallIntegerField()
    max_answers = SmallIntegerField()
    props = PollsManager.props()

    objects = PollsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Голосования'
