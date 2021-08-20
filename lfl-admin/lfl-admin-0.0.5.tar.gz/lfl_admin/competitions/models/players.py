import logging

from bitfield import BitField
from django.db.models import DateField, SmallIntegerField, OneToOneField, PROTECT, IntegerField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from lfl_admin.common.models.posts import Posts
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.user_ext.models.persons import Persons

logger = logging.getLogger(__name__)


class PlayersQuerySet(AuditQuerySet):
    pass


class PlayersManager(AuditManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'active'),  # 0
            ('shadow', 'shadow'),  # 1
            ('blocked', 'blocked'),  # 2
            ('disqualification', 'disqualification'),  # 3
            ('lockout', 'lockout'),  # 4
            ('delayed_lockout', 'delayed_lockout'),  # 5
            ('medical_lockout', 'medical_lockout'),  # 6
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
        return PlayersQuerySet(self.model, using=self._db)


class Players(AuditModel):
    amplua = ForeignKeyProtect(Posts)
    club = ForeignKeyProtect(Clubs)
    debut = DateField(null=True, blank=True)
    delayed_lockout_date = DateField(null=True, blank=True)
    editor = ForeignKeyProtect(User, null=True, blank=True)
    height = SmallIntegerField()
    included = DateField(null=True, blank=True)
    medical_admission_date = DateField(null=True, blank=True)
    number = SmallIntegerField(null=True, blank=True)
    person = OneToOneField(Persons, on_delete=PROTECT)
    size_of_photo = IntegerField()
    weight = SmallIntegerField()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            person=Persons.unknown(),
            defaults=dict(
                amplua=Posts.unknown(),
                club_id_now=Clubs.unknown(),
                height=0,
                size_of_photo=0,
                weight=0,
            )
        )
        return res

    props = PlayersManager.props()

    objects = PlayersManager()

    def __str__(self):
        return f'ID:{self.id} full_name = {self.person.user.get_full_name}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Игроки'
