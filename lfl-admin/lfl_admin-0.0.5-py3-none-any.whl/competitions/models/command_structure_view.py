import logging
from datetime import timedelta, date

from django.conf import settings
from django.db import transaction
from django.db.models import BooleanField
from django.utils import timezone

from isc_common import delAttr, setAttr
from isc_common.auth.models.user import User
from isc_common.datetime import DateToStr, DateToDateTime
from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from isc_common.number import model_2_dict
from isc_common.ws.webSocket import WebSocket
from lfl_admin.common.models.posts import Posts
from lfl_admin.competitions.models.calendar import Calendar
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.formation import Formation
from lfl_admin.competitions.models.player_histories import Player_histories, Player_historiesManager
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.tournaments import Tournaments
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class Command_structure_viewQuerySet(AuditQuerySet):
    def get_range_rows1(self, request, function=None, distinct_field_names=None, remove_fields=None):
        request = DSRequest(request=request)

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


class Command_structure_viewManager(AuditManager):

    @classmethod
    def refreshRows(cls, ids):
        if isinstance(ids, int):
            ids = [ids]
        records = [Command_structure_viewManager.getRecord(record) for record in Command_structure_view.objects.filter(id__in=ids)]
        WebSocket.row_refresh_grid(grid_id=settings.GRID_CONSTANTS.refresh_command_structure_view_grid_row, records=records)

    @classmethod
    def fullRows(cls, suffix=''):
        WebSocket.full_refresh_grid(grid_id=f'{settings.GRID_CONSTANTS.refresh_command_structure_view_grid}{suffix}')

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()

        return data

    def updateFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()

        with transaction.atomic():
            player_histories = Player_histories.objects.get(id=data.get('id'))

            hidden = data.get('hidden')
            if not hidden:
                hidden = player_histories.tournament.props.hidden.is_set

            props = player_histories.props

            if hidden is True:
                props |= Player_histories.props.hidden
            else:
                props &= ~Player_histories.props.hidden

            player_histories_dict = model_2_dict(player_histories)
            delAttr(player_histories_dict, 'id')
            player_id = data.get('player_id')

            if player_id is None:
                player_id = player_histories.player.id

            setAttr(player_histories_dict, 'player_id', player_id)
            setAttr(player_histories_dict, 'props', props._value)

            num = data.get('num')
            if num is None:
                num = player_histories.num

            setAttr(player_histories_dict, 'num', num)
            delAttr(player_histories_dict, 'club_id')
            delAttr(player_histories_dict, 'player_id')
            delAttr(player_histories_dict, 'match_id')
            delAttr(player_histories_dict, 'club_id_old')
            delAttr(player_histories_dict, 'match_id_old')
            delAttr(player_histories_dict, 'player_id_old')

            player_histories_clone, create = Player_histories.objects.update_or_create(
                club=player_histories.club,
                match=player_histories.match,
                player_id=player_id,
                defaults=player_histories_dict

            )
            record = Command_structure_view.objects.get(id=player_histories_clone.id)
            res = Command_structure_viewManager.getRecord(record)

            if create is True:
                player_histories.soft_delete()

            Command_structure_viewManager.fullRows()
            return res

    def deleteFromRequest(self, request, removed=None, ):
        request = DSRequest(request=request)
        res = 0
        tuple_ids = request.get_olds_tuple_ids()
        ids = []
        with transaction.atomic():
            for id, mode in tuple_ids:
                if mode == 'hide':
                    Player_histories.objects.filter(id=id).soft_delete()
                    res += 1
                elif mode == 'visible':
                    Player_histories.objects.filter(id=id).soft_restore()
                else:
                    query = Player_histories.objects.filter(id=id)
                    res += query.count()
                    query.soft_delete()
                ids.append(id)

            Command_structure_viewManager.refreshRows(ids=ids)

        return res

    def pasteFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        player_histories_ids = data.get('data')
        data_past = data.get('data_past')
        player_histories_past = Player_histories.objects.get(id=data_past.get('id'))

        with transaction.atomic():
            for player_histories in Player_histories.objects.filter(id__in=player_histories_ids):
                player_histories_dict = model_2_dict(player_histories)
                delAttr(player_histories_dict, 'id')
                delAttr(player_histories_dict, 'club_id')
                delAttr(player_histories_dict, 'player_id')
                delAttr(player_histories_dict, 'match_id')

                _, created = Player_histories.objects.update_or_create(
                    club=player_histories_past.club,
                    match=player_histories_past.match,
                    player=player_histories.player,
                    defaults=player_histories_dict
                )

            Command_structure_viewManager.fullRows()

        return dict(status=RPCResponseConstant.statusSuccess)

    @classmethod
    def getRecord(cls, record):
        res = {
            'age': f'{DateToStr(record.user.birthday)} ({(timezone.now() - DateToDateTime(record.user.birthday)) // timedelta(days=365)})' if isinstance(record.user.birthday, date) else None,
            'amplua__name': record.amplua.name,
            'amplua_id': record.amplua.id,
            'club__name': record.club.name,
            'club_id': record.club.id,
            'deleted': record.deleted_at is not None,
            'deliting': record.deliting,
            'editing': record.editing,
            'first_name': record.first_name,
            'hidden': record.hidden,
            'id': record.id,
            'last_name': record.last_name,
            'middle_name': record.middle_name,
            'num': record.num,
            'photo_real_name': record.photo_real_name,
            'photo_src': f'http://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.photo_image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}',
            'player__first_name': record.user.first_name,
            'player__last_name': record.user.last_name,
            'player__middle_name': record.user.middle_name,
            'region__name': record.region.name,
            'region_id': record.region.id,
        }
        return res

    def get_queryset(self):
        return Command_structure_viewQuerySet(self.model, using=self._db)


class Command_structure_view(AuditModel):
    amplua = ForeignKeyProtect(Posts)
    club = ForeignKeyProtect(Clubs)
    first_name = NameField(null=True, blank=True)
    formation = ForeignKeyProtect(Formation)
    hidden = BooleanField()
    last_name = NameField(null=True, blank=True)
    match = ForeignKeyProtect(Calendar)
    middle_name = NameField(null=True, blank=True)
    num = CodeField(null=True, blank=True)
    photo_image_src = NameField()
    photo_img = NameField()
    photo_real_name = NameField()
    player = ForeignKeyProtect(Players)
    props = Player_historiesManager.props()
    region = ForeignKeyProtect(Regions)
    user = ForeignKeyProtect(User)
    tournament = ForeignKeyProtect(Tournaments)

    objects = Command_structure_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Состав комманды'
        db_table = 'competitions_command_structure_view'
        managed = False
