import logging

from bitfield import BitField

from isc_common.common import undefined
from isc_common.fields.code_field import CodeField
from isc_common.models.base_ref import BaseRefHierarcyManager, BaseRefHierarcy, BaseRefHierarcyQuerySet

logger = logging.getLogger(__name__)


class PostsQuerySet(BaseRefHierarcyQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class PostsManager(BaseRefHierarcyManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('administrator', 'administrator'),  # 1
            ('player', 'player'),  # 1
        ), default=0, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'parent_id': record.parent.id if record.parent else None,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return PostsQuerySet(self.model, using=self._db)


class Posts(BaseRefHierarcy):
    code = CodeField(db_index=True, unique=True)
    props = PostsManager.props()
    objects = PostsManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(code=undefined)
        return res

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Должности'
