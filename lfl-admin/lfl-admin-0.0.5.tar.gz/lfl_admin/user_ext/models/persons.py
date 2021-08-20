import logging

from bitfield import BitField
from django.db.models import OneToOneField, PROTECT

from isc_common import delAttr
from isc_common.auth.models.abstract_user import NonamedUserException
from isc_common.auth.models.user import User
from isc_common.fields.description_field import DescriptionField
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldIds
from isc_common.models.audit_ex import AuditModelEx

logger = logging.getLogger(__name__)


class PersonsQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class PersonsManager(AuditManager):
    def getOptionalExt(self, *args, **kwargs):
        from lfl_admin.region.models.regions import Regions
        from lfl_admin.user_ext.models.users_regions import Users_regions
        from isc_common.auth.models.user import User

        region = kwargs.get('region')
        birthday = kwargs.get('birthday')
        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')
        middle_name = kwargs.get('middle_name')
        old_id = kwargs.get('old_id')

        delAttr(kwargs, 'region')
        delAttr(kwargs, 'birthday')
        delAttr(kwargs, 'first_name')
        delAttr(kwargs, 'last_name')
        delAttr(kwargs, 'middle_name')
        delAttr(kwargs, 'old_id')

        try:
            person = self.getOptional(*args, **kwargs)
        except Persons.MultipleObjectsReturned:
            for person in self.filter(*args, **kwargs):
                if len(person.old_ids) > 1:
                    person.old_ids = list(filter(lambda x: x != old_id, person.old_ids))
                    person.save()
            person = self.getOptional(*args, **kwargs)

        if not isinstance(region, Regions):
            raise Exception('Not regions')

        if person is None:
            users = User.objects.filter(
                birthday=birthday,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
            )

            users_regions = Users_regions.objects.filter(user__in=users, region=region)

            if users_regions.count() == 0:
                try:
                    username = User.full_name(
                        birthday=birthday,
                        first_name=first_name,
                        last_name=last_name,
                        middle_name=middle_name,
                        translit=True,
                    )

                    user, _ = User.objects.get_or_create(
                        username=f'{username}_{region.id}',
                        defaults=dict(
                            birthday=birthday,
                            first_name=first_name,
                            last_name=last_name,
                            middle_name=middle_name,
                        )
                    )

                    person, _ = Persons.objects.get_or_create(user=user)
                    user_region, _ = Users_regions.objects.get_or_create(user=user, region=region)
                except NonamedUserException:
                    person = Persons.objects.get(user=User.unknown())
            else:
                person, _ = Persons.objects.get_or_create(user=users[0])
        return person

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'active'),  # 1
            ('archive', 'archive'),  # 1
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
        return PersonsQuerySet(self.model, using=self._db)

    def get_user(self, old_ids):
        if isinstance(old_ids, int):
            old_ids = [old_ids]
        res = Persons.objects.getOptional(old_ids__overlap=old_ids)
        if res is None:
            return None
        else:
            return res.user


class Persons(AuditModelEx, Model_withOldIds):
    description = DescriptionField()
    props = PersonsManager.props()
    user = OneToOneField(User, on_delete=PROTECT)

    objects = PersonsManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(user=User.unknown())
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Персоны'
