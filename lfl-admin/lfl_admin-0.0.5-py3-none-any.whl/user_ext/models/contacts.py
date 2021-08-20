import logging

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldIds
from isc_common.models.audit_ex import AuditModelEx
from lfl_admin.competitions.models.clubs import Clubs

logger = logging.getLogger(__name__)


class ContactsQuerySet(AuditQuerySet):
    pass


class ContactsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'parent': record.parent.id if record.parent else None,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return ContactsQuerySet(self.model, using=self._db)


class Contacts(AuditModelEx, Model_withOldIds):
    club = ForeignKeyProtect(Clubs)
    user = ForeignKeyProtect(User)
    objects = ContactsManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(user=User.unknown(), club=Clubs.unknown())
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Контакты'
        unique_together = (('club', 'user'),)
