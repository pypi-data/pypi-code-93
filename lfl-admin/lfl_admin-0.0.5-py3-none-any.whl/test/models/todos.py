import logging

from django.db.models import CharField

from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet

logger = logging.getLogger(__name__)


class TodosQuerySet(AuditQuerySet):
    pass


class TodosManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': str(record.id),
            'title': record.title,
        }
        return res

    def get_queryset(self):
        return TodosQuerySet(self.model, using=self._db)


class Todos(AuditModel):
    title = CharField(max_length=255)
    objects = TodosManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Тест объект Todo'
