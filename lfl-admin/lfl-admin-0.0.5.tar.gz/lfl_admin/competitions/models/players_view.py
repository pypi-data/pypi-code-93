import logging
from datetime import timedelta, date

from django.conf import settings
from django.db.models import DateField, SmallIntegerField, OneToOneField, PROTECT, IntegerField, BooleanField, DateTimeField
from django.utils import timezone

from isc_common.auth.models.user import User
from isc_common.datetime import DateToDateTime, DateToStr
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from isc_common.number import DelProps
from lfl_admin.common.models.posts import Posts
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.players import PlayersManager
from lfl_admin.competitions.models.tournaments import Tournaments
from lfl_admin.region.models.regions import Regions
from lfl_admin.user_ext.models.persons import Persons

logger = logging.getLogger(__name__)


class PlayersQuerySet(AuditQuerySet):
    def prepare_request(self, request):
        from lfl_admin.competitions.models.player_histories import Player_histories

        data = request.get_data()

        division_ids = data.get('division_ids')
        if division_ids is None:
            tounament_ids = data.get('tournaments_ids')
        else:
            tounament_ids = list(set(map(lambda x: x.get('id'), Tournaments.objects.filter(division_id__in=division_ids, props=Tournaments.props.active).values('id'))))

        if tounament_ids is not None:
            player_id = list(set(map(lambda x: x.get('player'), Player_histories.objects.filter(tournament_id__in=tounament_ids).values('player'))))
            if len(player_id) == 0:
                player_id = [-1]

            request.set_data(dict(id=player_id))
        return request

    def get_info(self, request, *args):
        request = DSRequest(request=request)
        request = self.prepare_request(request)

        criteria = self.get_criteria(json=request.json)
        cnt = super().filter(*args, criteria).count()
        cnt_all = super().filter().count()
        return dict(qty_rows=cnt, all_rows=cnt_all)

    def get_range_rows1(self, request, function=None, distinct_field_names=None, remove_fields=None):
        request = DSRequest(request=request)
        request = self.prepare_request(request)

        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
        res = self.get_range_rows(
            start=request.startRow,
            end=request.endRow,
            function=function,
            distinct_field_names=distinct_field_names,
            json=request.json,
            criteria=request.get_criteria(),
            user=request.user
        )
        return res


class Players_viewManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'active': record.active,
            'amplua__name': record.amplua.name,
            'amplua_id': record.amplua.id,
            'age': f'{DateToStr(record.birthday)} ({(timezone.now() - DateToDateTime(record.birthday)) // timedelta(days=365)})' if isinstance(record.birthday, date) else None,
            'club__name': record.club.name,
            'club_id': record.club.id,
            'deliting': record.deliting,
            'editing': record.editing,
            'first_name': record.first_name,
            'id': record.id,
            'last_name': record.last_name,
            'middle_name': record.middle_name,
            'photo_real_name': record.photo_real_name,
            'photo_src': f'http://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.photo_image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}',
            'props': record.props,
            'region__name': record.region.name,
            'region_id': record.region.id,
        }
        return DelProps(res)

    def get_queryset(self):
        return PlayersQuerySet(self.model, using=self._db)


class Players_view(AuditModel):
    active = BooleanField()
    amplua = ForeignKeyProtect(Posts)
    birthday = DateTimeField(blank=True, null=True)
    club = ForeignKeyProtect(Clubs)
    debut = DateField(null=True, blank=True)
    delayed_lockout_date = DateField(null=True, blank=True)
    editor = ForeignKeyProtect(User, null=True, blank=True)
    first_name = NameField()
    height = SmallIntegerField()
    included = DateField(null=True, blank=True)
    last_name = NameField()
    medical_admission_date = DateField(null=True, blank=True)
    middle_name = NameField()
    number = SmallIntegerField(null=True, blank=True)
    person = OneToOneField(Persons, on_delete=PROTECT)
    photo_image_src = NameField()
    photo_real_name = NameField()
    region = ForeignKeyProtect(Regions, null=True, blank=True)
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

    objects = Players_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Игроки'
        db_table = 'competitions_players_view'
        managed = False
