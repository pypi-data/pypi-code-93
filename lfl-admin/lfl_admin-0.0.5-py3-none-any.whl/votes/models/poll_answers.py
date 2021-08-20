import logging

from bitfield import BitField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet
from lfl_admin.votes.models.polls import Polls

logger = logging.getLogger(__name__)


class Poll_answersQuerySet(BaseRefQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Poll_answersManager(BaseRefManager):
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
        return Poll_answersQuerySet(self.model, using=self._db)


class Poll_answers(BaseRef):
    editor = ForeignKeyProtect(User, null=True, blank=True)
    poll = ForeignKeyProtect(Polls)
    props = Poll_answersManager.props()

    objects = Poll_answersManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Ответы на голосовании'
