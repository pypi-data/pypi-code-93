import logging

from bitfield import BitField
from django.db.models import DateTimeField, SmallIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldId
from isc_common.models.base_ref import Hierarcy
from lfl_admin.competitions.models.calendar import Calendar
from lfl_admin.competitions.models.leagues import Leagues
from lfl_admin.competitions.models.tournaments import Tournaments
from lfl_admin.decor.models.news_type import News_type
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class NewsQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class NewsManager(AuditManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'active'),  # 1
            ('disable_editor', 'disable_editor'),  # 1
            ('fixed_position', 'fixed_position'),  # 1
            ('in_bottom', 'in_bottom'),  # 1
            ('in_middle', 'in_middle'),  # 1
            ('in_top', 'in_top'),  # 1
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
        return NewsQuerySet(self.model, using=self._db)


class News(Hierarcy, Model_withOldId):
    admin = ForeignKeyProtect(User, related_name='News_admin')
    created = ForeignKeyProtect(User, related_name='News_created')
    date = DateTimeField(blank=True, null=True)
    league = ForeignKeyProtect(Leagues)
    match = ForeignKeyProtect(Calendar)
    position = SmallIntegerField()
    icon = SmallIntegerField()
    props = NewsManager.props()
    region = ForeignKeyProtect(Regions)
    tournament = ForeignKeyProtect(Tournaments)
    type = ForeignKeyProtect(News_type)

    objects = NewsManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            admin=User.unknown(),
            created=User.unknown(),
            league=Leagues.unknown(),
            match=Calendar.unknown(),
            position=0,
            icon=0,
            region=Regions.unknown(),
            tournament=Tournaments.unknown(),
            type=News_type.unknown(),
        )
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Новости, встраиваемые блоки, видео'
