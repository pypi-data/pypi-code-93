import logging

from bitfield import BitField
from django.db.models import DateField, OneToOneField, PROTECT

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldIds
from isc_common.models.audit_ex import AuditModelEx
from lfl_admin.common.models.posts import Posts
from lfl_admin.user_ext.models.contacts import Contacts
from lfl_admin.user_ext.models.persons import Persons

logger = logging.getLogger(__name__)


class RefereesQuerySet(AuditQuerySet):
    pass


class RefereesManager(AuditManager):

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
        return RefereesQuerySet(self.model, using=self._db)


class Referees(AuditModelEx, Model_withOldIds):
    contact = ForeignKeyProtect(Contacts)
    debut = DateField(blank=True, null=True)
    person = OneToOneField(Persons, on_delete=PROTECT)
    props = RefereesManager.props()
    referee_post = ForeignKeyProtect(Posts)

    objects = RefereesManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(person=Persons.unknown(), defaults=dict(contact=Contacts.unknown(), referee_post=Posts.unknown()))
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Судьи'
