import logging

from django.conf import settings
from django.db.models import DecimalField

from isc_common.common import blinkString
from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditQuerySet, AuditManager
from isc_common.number import DelProps
from lfl_admin.common.models.posts import Posts
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.players import Players

logger = logging.getLogger(__name__)


class Raiting_of_players_viewQuerySet(AuditQuerySet):
    def prepare_request(self, request):
        # data = request.get_data()
        #
        # division_ids = data.get('division_ids')
        # tournament_ids = data.get('tournament_ids')
        #
        # division_id = list(set(map(lambda x: x.get('division'), Raiting_of_players_division.objects.filter(raiting_id__in=ids).values('division'))))
        # if len(division_id) == 0:
        #     division_id = [-1]
        #
        # delAttr(request.json.get('data'), 'ids')
        # setAttr(request.json.get('data'), 'id', division_id)
        return request

    def get_info(self, request, *args):
        request = DSRequest(request=request)
        request = self.prepare_request(request)

        criteria = self.get_criteria(json=request.json)
        cnt = super().filter(*args, criteria).count()
        cnt_all = super().filter().count()
        return dict(qty_rows=cnt, all_rows=cnt_all)


class Raiting_of_players_viewManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'amplua__name': record.amplua.name,
            'amplua_id': record.amplua.id,
            'club__name': record.club.name,
            'club_id': record.club.id,
            'deliting': record.deliting,
            'editing': record.editing,
            'FIO': record.FIO,
            'num': record.num,
            'id': record.id,
            'KF': record.KF,
            'kf_bombar': record.kf_bombar,
            'kf_not_wins': record.kf_not_wins,
            'kf_opyt': record.kf_opyt,
            'kf_plus_minus': record.kf_plus_minus,
            'kf_propusch_com': record.kf_propusch_com,
            'kf_wins': record.kf_wins,
            'kf_zabito_com': record.kf_zabito_com,
            'lastmodified': record.lastmodified,
            'mid_propusch_com': record.mid_propusch_com,
            'mid_zabito_com': record.mid_zabito_com,
            'not_win_cnt': record.not_win_cnt,
            'pers_not_wins': record.pers_not_wins,
            'pers_wins': record.pers_wins,
            'photo_real_name': record.photo_real_name,
            'photo_src': f'http://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.photo_image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}',
            'player_id': record.player.id,
            'plays': record.plays,
            'plus_minus': record.plus_minus,
            'propusch_com': record.propusch_com,
            'raiting': blinkString(record.raiting, blink=False, bold=True),
            'standoff_cnt': record.standoff_cnt,
            'win_cnt': record.win_cnt,
            'zabito_com': record.zabito_com,
            'zabito_play': record.zabito_play,
        }
        return DelProps(res)

    def get_queryset(self):
        return Raiting_of_players_viewQuerySet(self.model, using=self._db)


class Raiting_of_players_view(AuditModel):
    amplua = ForeignKeyProtect(Posts)
    club = ForeignKeyProtect(Clubs)
    FIO = NameField()
    num = CodeField()
    KF = CodeField()
    kf_bombar = DecimalField(max_digits=5, decimal_places=2, )
    kf_not_wins = DecimalField(max_digits=5, decimal_places=2, )
    kf_opyt = DecimalField(max_digits=5, decimal_places=2, )
    kf_plus_minus = DecimalField(max_digits=5, decimal_places=2, )
    kf_propusch_com = DecimalField(max_digits=5, decimal_places=2, )
    kf_wins = DecimalField(max_digits=5, decimal_places=2, )
    kf_zabito_com = DecimalField(max_digits=5, decimal_places=2, )
    mid_propusch_com = DecimalField(max_digits=5, decimal_places=2, )
    mid_zabito_com = DecimalField(max_digits=5, decimal_places=2, )
    not_win_cnt = DecimalField(max_digits=5, decimal_places=2, )
    plays = DecimalField(max_digits=5, decimal_places=2, )
    pers_not_wins = DecimalField(max_digits=5, decimal_places=2, )
    pers_wins = DecimalField(max_digits=5, decimal_places=2, )
    photo_image_src = NameField()
    photo_real_name = NameField()
    player = ForeignKeyProtect(Players)
    plus_minus = DecimalField(max_digits=5, decimal_places=2, )
    propusch_com = DecimalField(max_digits=5, decimal_places=2, )
    raiting = DecimalField(max_digits=5, decimal_places=2, )
    standoff_cnt = DecimalField(verbose_name='Ничьих', max_digits=5, decimal_places=2, )
    win_cnt = DecimalField(max_digits=5, decimal_places=2, )
    zabito_com = DecimalField(max_digits=5, decimal_places=2, )
    zabito_play = DecimalField(max_digits=5, decimal_places=2, )

    objects = Raiting_of_players_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Рейтинг футболистов'
        db_table = 'statistic_raiting_of_players_view'
        managed = False
