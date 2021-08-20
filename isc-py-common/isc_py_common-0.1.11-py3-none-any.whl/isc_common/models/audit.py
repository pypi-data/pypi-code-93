import logging

from django.contrib.postgres.fields import ArrayField
from django.db.models import Model, BooleanField, BigAutoField, DateTimeField, Transform, CharField, TextField, BigIntegerField
from django.utils import timezone
from transliterate import translit
from transliterate.exceptions import LanguageDetectionError

from isc_common import setAttr, delAttr
from isc_common.managers.common_manager import CommonManager, CommonQuerySet

logger = logging.getLogger(__name__)


class Model_withOldId(Model):
    old_id = BigIntegerField(db_index=True, null=True, blank=True, unique=True)

    class Meta:
        abstract = True


class Model_withOldIds(Model):
    old_ids = ArrayField(BigIntegerField(), null=True, blank=True, unique=True)

    class Meta:
        abstract = True


class AuditQuerySet(CommonQuerySet):
    def getOptional(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

    def _check_ed_izm_qty(self, **kwargs):
        if kwargs.get('ed_izm') is not None and kwargs.get('qty') is None or kwargs.get('ed_izm') is None and kwargs.get('qty') is not None:
            raise Exception(f'Единица измерения не может быть указана без количества')

    def __init__(self, model=None, query=None, using=None, hints=None, alive_only=True):
        self.alive_only = alive_only
        super().__init__(model=model, query=query, using=using, hints=hints, alive_only=alive_only)

    def rearrange_parent(self, json):
        # _criteria = json.get('data').get('criteria')
        # if isinstance(_criteria, list):
        #     for criterion in _criteria:
        #         if criterion.get('fieldName') == 'parent_id':
        #             item_id = criterion.get('value')
        #             if (item_id, int):
        #                 criteria_lst = [criterion for criterion in _criteria if criterion.get('fieldName') == 'parent_id' and criterion.get('value') is not None]
        #                 if len(criteria_lst) > 0:
        #                     setAttr(json.get('data'), 'criteria', criteria_lst)
        return json

    def soft_delete(self):
        res = super().update(deleted_at=timezone.now())
        if res > 0:
            return self
        else:
            return None

    def soft_restore(self):
        res = super().update(deleted_at=None)
        return res

    def hard_delete(self):
        res = super().delete()
        return res

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)

    def update(self, **kwargs):
        if kwargs.get('lastmodified') is None:
            setAttr(kwargs, 'lastmodified', timezone.now())
        return super().update(**kwargs)


class AuditManager(CommonManager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return AuditQuerySet(model=self.model, alive_only=self.alive_only).filter(deleted_at=None)
        return AuditQuerySet(model=self.model, alive_only=self.alive_only)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

    def soft_delete(self):
        return self.get_queryset().soft_delete()

    def soft_restore(self):
        return self.get_queryset().soft_restore()

    def getOptional(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

    def getOr(self, *args, **kwargs):
        alternative = kwargs.get('alternative')
        try:
            delAttr(kwargs, 'alternative')
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            if not callable(alternative):
                raise Exception('alternative must be callable')
            return alternative()
        except self.model.MultipleObjectsReturned as ex:
            old_ids = kwargs.get('old_ids__overlap')
            if old_ids is None:
                raise ex
            if len(old_ids) > 1:
                raise ex

            old_id=old_ids[0]

            for item in self.filter(*args, **kwargs):
                if len(item.old_ids) > 1:
                    item.old_ids = list(filter(lambda x: x != old_id, item.old_ids))
                    item.save()

            return self.get(*args, **kwargs)


class Manager(CommonManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        return AuditQuerySet(model=self.model)


class AuditModel(Model):
    id = BigAutoField(primary_key=True, verbose_name="Идентификатор")
    deleted_at = DateTimeField(verbose_name="Дата мягкого удаления", null=True, blank=True, db_index=True)
    editing = BooleanField(verbose_name="Возможность редактирования", default=True)
    deliting = BooleanField(verbose_name="Возможность удаления", default=True)
    lastmodified = DateTimeField(verbose_name='Последнее обновление', editable=False, db_index=True, default=timezone.now)

    @classmethod
    def uncapitalize(cls, str):
        from isc_common.common.functions import uncapitalize
        return uncapitalize(str)

    @classmethod
    def translit(cls, value):
        if isinstance(value, int):
            return str(value)
        try:
            return cls.uncapitalize(translit(value, reversed=True).replace("'", '').replace(' ', '_').replace('.', '_'))
        except LanguageDetectionError:
            return cls.uncapitalize(value.replace("'", '').replace(' ', '_').replace('.', '_'))

    @classmethod
    def dbl_qutes_str(cls, str):
        from isc_common.common.functions import dbl_qutes_str
        return dbl_qutes_str(str)

    @classmethod
    def qutes_str(cls, str):
        from isc_common.common.functions import qutes_str
        return qutes_str(str)

    @property
    def idHidden(self):
        return not self is None

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
        return self

    def soft_restore(self):
        self.deleted_at = None
        self.save()
        return self

    objects = AuditManager()
    all_objects = AuditManager(alive_only=False)


class Dbl_spacesValue(Transform):
    lookup_name = 'delete_dbl_spaces'
    function = 'delete_dbl_spaces'


CharField.register_lookup(Dbl_spacesValue)
TextField.register_lookup(Dbl_spacesValue)


class Trim_Value(Transform):
    lookup_name = 'trim'
    function = 'trim'


CharField.register_lookup(Trim_Value)
TextField.register_lookup(Trim_Value)


class Upper_Value(Transform):
    lookup_name = 'upper'
    function = 'upper'


CharField.register_lookup(Upper_Value)
TextField.register_lookup(Upper_Value)
