import logging

from bitfield import BitField
from django.db.models import SmallIntegerField
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldIds
from isc_common.models.audit_ex import AuditModelEx

from lfl_admin.common.models.posts import Posts
from lfl_admin.competitions.models.clubs import Clubs

logger = logging.getLogger(__name__)


class Club_contactsQuerySet(AuditQuerySet):
    pass


class Club_contactsManager(AuditManager):
    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'active'),  # 1
            ('leader', 'leader'),  # 1
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
        return Club_contactsQuerySet(self.model, using=self._db)


class Club_contacts(AuditModelEx, Model_withOldIds):
    club = ForeignKeyProtect(Clubs)
    person = ForeignKeyProtect(User)
    post = ForeignKeyProtect(Posts)
    priority = SmallIntegerField(default=0)
    props = Club_contactsManager.props()

    objects = Club_contactsManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            club=Clubs.unknown(),
            person=User.unknown(),
            post=Posts.unknown(),
            props=0
        )
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс-таблица'
        unique_together = (('club', 'person', 'post', 'priority', 'props'),)
