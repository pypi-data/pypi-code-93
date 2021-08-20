import logging

from bitfield import BitField

from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager
from isc_common.models.phones import Phones, Model_phonesQuerySet
from lfl_admin.user_ext.models.contacts import Contacts

logger = logging.getLogger(__name__)


class Contacts_phonesQuerySet(Model_phonesQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Contacts_phonesManager(AuditManager):
    @classmethod
    def props(cls):
        return BitField(flags=(
            ('main', 'Главная'),  # 1
        ), default=0, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Contacts_phonesQuerySet(self.model, using=self._db)


class Contacts_phones(AuditModel):
    code = CodeStrictField()
    contact = ForeignKeyProtect(Contacts)
    phone = ForeignKeyProtect(Phones)
    props = Contacts_phonesManager.props()

    objects = Contacts_phonesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Администрация клуба'
        unique_together = (('code', 'contact', 'phone'),)
