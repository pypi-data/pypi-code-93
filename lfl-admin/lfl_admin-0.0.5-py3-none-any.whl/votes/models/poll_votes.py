import logging

from django.db.models import DateTimeField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from lfl_admin.votes.models.poll_answers import Poll_answers
from lfl_admin.votes.models.polls import Polls

logger = logging.getLogger(__name__)


class Poll_votesQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Poll_votesManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Poll_votesQuerySet(self.model, using=self._db)


class Poll_votes(AuditModel):
    answer = ForeignKeyProtect(Poll_answers)
    author = ForeignKeyProtect(User)
    poll = ForeignKeyProtect(Polls)
    time = DateTimeField()

    objects = Poll_votesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Подсчет голосов'
