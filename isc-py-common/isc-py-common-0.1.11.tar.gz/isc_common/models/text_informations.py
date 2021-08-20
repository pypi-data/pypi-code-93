import logging

from django.db.models import TextField

from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet

logger = logging.getLogger(__name__)


class Model_text_informationsQuerySet(AuditQuerySet):

    def update_or_create(self, defaults=None, **kwargs):
        text = defaults.get('text')

        if text != '' and text is not None:
            try:
                item = super().get(**kwargs)
                text_item, _ = Text_informations.objects.update_or_create(id=item.id, defaults=dict(text=text))
            except self.model.DoesNotExist:
                text_informations = list(Text_informations.objects.filter(text=text))
                if len(text_informations) > 0:
                    text_item = text_informations[0]
                else:
                    text_item = Text_informations.objects.create(text=text)

            defaults = dict(text=text_item)
            return super().update_or_create(defaults=defaults, **kwargs)


class Text_informationsQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Text_informationsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Text_informationsQuerySet(self.model, using=self._db)


class Text_informations(AuditModel):
    text = TextField(db_index=True)

    objects = Text_informationsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Якоря'
