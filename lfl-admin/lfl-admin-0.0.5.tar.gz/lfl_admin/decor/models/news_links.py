import logging

from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager
from isc_common.models.links import Model_linksQuerySet, Links
from lfl_admin.decor.models.news import News

logger = logging.getLogger(__name__)


class News_linksQuerySet(Model_linksQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class News_linksManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return News_linksQuerySet(self.model, using=self._db)


class News_links(AuditModel):
    code = CodeStrictField()
    link = ForeignKeyProtect(Links)
    new = ForeignKeyProtect(News)

    objects = News_linksManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('link', 'new', 'code'),)
