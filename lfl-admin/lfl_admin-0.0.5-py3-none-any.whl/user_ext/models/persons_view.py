import logging

from django.conf import settings
from django.db.models import OneToOneField, PROTECT, BooleanField, DateField

from isc_common.auth.models.user import User
from isc_common.fields.description_field import DescriptionField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldIds
from isc_common.models.audit_ex import AuditModelEx
from isc_common.number import DelProps
from lfl_admin.region.models.regions import Regions
from lfl_admin.user_ext.models.persons import PersonsManager

logger = logging.getLogger(__name__)


class Persons_viewQuerySet(AuditQuerySet):
    pass


class Persons_viewManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'active': record.active,
            'archive': record.archive,
            'birthday': record.birthday,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'first_name': record.first_name,
            'id': record.id,
            'last_name': record.last_name,
            'middle_name': record.middle_name,
            'props': record.props,
            'region__name': record.region.name,
            'region_id': record.region.id,
            'photo_real_name': record.photo_real_name,
            'photo_src': f'http://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.photo_image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}',
        }
        return DelProps(res)

    def get_queryset(self):
        return Persons_viewQuerySet(self.model, using=self._db)


class Persons_view(AuditModelEx, Model_withOldIds):
    active = BooleanField()
    archive = BooleanField()
    birthday = DateField(blank=True, null=True)
    description = DescriptionField()
    first_name = NameField()
    last_name = NameField()
    middle_name = NameField()
    photo_image_src = NameField()
    photo_real_name = NameField()
    props = PersonsManager.props()
    region = ForeignKeyProtect(Regions, null=True, blank=True)
    user = OneToOneField(User, on_delete=PROTECT)

    objects = Persons_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Персоны'
        db_table = 'user_ext_persons_view'
        managed = False
