import logging

from bitfield import BitField
from django.db import transaction
from django.db.models import OneToOneField, PROTECT, DateTimeField, ProtectedError

from isc_common import delAttr, dictinct_list, setAttr
from isc_common.auth.models.user import User
from isc_common.common.functions import get_dict_only_model_field
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel, Model_withOldId
from isc_common.ssh.ssh_client import SSH_Client_settings

logger = logging.getLogger(__name__)


class AdministratorsQuerySet(AuditQuerySet):
    pass


class AdministratorsManager(AuditManager):
    def updateFromRequest(self, request):
        from isc_common.models.users_images import Users_images
        from isc_common.models.users_old_images import Users_old_images

        with transaction.atomic():
            request = DSRequest(request=request)
            props = 0
            data = request.get_data()

            data = self.check_data_for_multi_select(data=data)
            _data = data.copy()

            delAttr(data, 'usergroup')
            oldValues = request.get_oldValues()

            _oldValues = oldValues.get('data')
            if not _oldValues:
                _oldValues = oldValues

            _oldValues = self.check_data_for_multi_select(data=_oldValues)

            data = self._remove_prop_(data)
            values = [item for item in dictinct_list(set(_oldValues) - set(data)) if not item.startswith('_')]
            for item in values:
                setAttr(data, item, None)

            user_id = data.get('user_id')
            register_date = data.get('register_date')
            deliting = data.get('deliting')
            editing = data.get('editing')

            id = data.get('id')
            active = data.get('active')

            if active is True:
                props |= Administrators.props.active

            User.objects.filter(id=user_id).update(**get_dict_only_model_field(data=data, model=User, exclude=['password']))

            super().filter(id=id).update(props=props, register_date=register_date, editing=editing, deliting=deliting)

            if _data.get('photo_real_name') == 'DELETED':
                SSH_CLIENT = SSH_Client_settings()
                for users_image in Users_images.objects.filter(main_model_id=user_id):
                    ex = SSH_CLIENT.exists(str(users_image.image.attfile))
                    if ex is True:
                        Users_old_images.objects.get_or_create(main_model_id=user_id, image=users_image.image)

                    image = users_image.image
                    users_image.delete()

                    if ex is False:
                        try:
                            image.delete()
                        except ProtectedError:
                            pass

            user = User.objects.get(id=user_id)
            if user.check_password(data.get('password')) is False:
                user.set_password(data.get('password'))
                user.save()
                user = User.objects.get(id=user_id)
                setAttr(data, 'password', user.password)
                setAttr(data, 'short_name', user.get_short_name)

            # setAttr(data, 'ts', time.time())
        return _data

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'Актуальность'),  # 1
            ('send_email', 'send_email'),  # 2
            ('kdk_fine_deleting', 'kdk_fine_deleting'),  # 4
            ('person_editing', 'person_editing'),  # 8
            ('all_news_access', 'all_news_access'),  # 16
            ('public_access', 'public_access'),  # 32
            ('transfer_right', 'transfer_right'),  # 64
            ('news', 'news'),  # 128
            ('documents', 'documents'),  # 256
            ('official', 'official'),  # 512
            ('video', 'video'),  # 1024
            ('blocks', 'blocks'),  # 2048
            ('upload', 'upload'),  # 4096
            ('tournament_members', 'tournament_members'),  # 8192
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
        return AdministratorsQuerySet(self.model, using=self._db)

    def get_user(self, old_id):
        editor = super().getOptional(old_id=old_id)
        if editor is None:
            return None
        return editor.user


class Administrators(AuditModel, Model_withOldId):
    editor = ForeignKeyProtect(User, related_name='Administrators_editor', null=True, blank=True)
    register_date = DateTimeField(null=True, blank=True)
    user = OneToOneField(User, on_delete=PROTECT)

    props = AdministratorsManager.props()

    objects = AdministratorsManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(user=User.unknown())
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс-таблица'
