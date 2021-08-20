import logging

from isc_common import setAttr, delAttr
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.inventory.models.clothes import Clothes

logger = logging.getLogger(__name__)


class Clothes_clubsQuerySet(AuditQuerySet):

    def update_or_create(self, defaults=None, **kwargs):
        from lfl_admin.inventory.models.clothes_type import Clothes_type

        clothes_type = kwargs.get('clothes_type')
        code = kwargs.get('code')
        delAttr(kwargs, 'clothes_type')

        clothes_content = kwargs.get('clothes_content')
        delAttr(kwargs, 'clothes_content')

        if clothes_type == '' or clothes_type is None:
            return None, None

        if clothes_content == '' or clothes_content is None:
            return None, None

        clothes_type, _ = Clothes_type.objects.update_or_create(code=clothes_type, defaults=dict(name=clothes_type))
        cloth, _ = Clothes.objects.update_or_create(clothes_type=clothes_type, code=code if code is not None else AuditModel.translit(clothes_content), defaults=dict(name=clothes_content))
        setAttr(kwargs, 'cloth', cloth)

        return super().update_or_create(defaults=defaults, **kwargs)


class Clothes_clubsManager(AuditManager):

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
        return Clothes_clubsQuerySet(self.model, using=self._db)


class Clothes_clubs(AuditModel):
    code = CodeStrictField()
    club = ForeignKeyProtect(Clubs)
    cloth = ForeignKeyProtect(Clothes)

    objects = Clothes_clubsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('club', 'cloth', 'code'),)
