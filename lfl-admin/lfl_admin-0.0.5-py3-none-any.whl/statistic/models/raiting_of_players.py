import logging

from django.db import transaction
from django.db.models import DecimalField

from isc_common.bit import TurnBitOn
from isc_common.common import blinkString
from isc_common.common.functions import ExecuteStoredProcRows
from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditQuerySet, AuditManager
from isc_common.progress import managed_progress, ProgressDroped, progress_deleted
from lfl_admin.common.models.posts import Posts
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.players import Players

logger = logging.getLogger(__name__)


class Raiting_of_playersQuerySet(AuditQuerySet):
    pass


class Raiting_of_playersManager(AuditManager):

    def calcStaticFromRequest(self, request):
        from lfl_admin.competitions.models.tournaments import Tournaments
        from lfl_admin.statistic.models.raiting_of_players_division import Raiting_of_players_division
        from lfl_admin.statistic.models.raiting_of_players_tournamet import Raiting_of_players_tournamet

        request = DSRequest(request=request)

        tournament_ids = None
        division_ids = None
        players_ids = None

        data = request.get_data()
        d = data.get('d')
        if d is not None:
            tournament_ids = d.get('tournaments_ids')
            division_ids = d.get('division_ids')
            players_ids = data.get('players_ids')

        res = []
        if isinstance(players_ids, list) and (isinstance(tournament_ids, list) or isinstance(division_ids, list)):
            if not isinstance(tournament_ids, list):
                tournament_ids = list(set(map(lambda x: x.get('id'), Tournaments.objects.filter(division_id__in=division_ids, props=Tournaments.props.active).values('id'))))

            with transaction.atomic():
                with managed_progress(
                        id=f'calcStaticFromRequest_{request.user.id}',
                        qty=len(players_ids),
                        user=request.user,
                        message='<h4>Вычисление рейтинга</h4>',
                        title='Выполнено',
                        props=TurnBitOn(0, 0)
                ) as progress:
                    for players_id in players_ids:
                        user = Players.objects.get(id=players_id).person.user
                        progress.setContentsLabel(content=blinkString(f'Вычисление рейтинга: {user.get_full_name}', blink=False, bold=True))

                        rows = ExecuteStoredProcRows('raiting_of_players', [tournament_ids, players_id])
                        for row in rows:
                            FIO, num, KF, kf_bombar, kf_not_wins, kf_opyt, kf_plus_minus, kf_propusch_com, kf_zabito_com, mid_propusch_com, mid_zabito_com, plays, pers_not_wins, pers_wins, plus_minus, propusch_com, raiting, standoff_cnt, kf_wins, zabito_com, zabito_play, amplua_id, club_id, player_id, win_cnt, not_win_cnt = row
                            raiting = Raiting_of_players.objects.create(
                                amplua_id=amplua_id,
                                club_id=club_id,
                                FIO=FIO,
                                num=num,
                                KF=KF,
                                kf_bombar=kf_bombar,
                                kf_not_wins=kf_not_wins,
                                kf_opyt=kf_opyt,
                                kf_plus_minus=kf_plus_minus if kf_plus_minus is not None else 0,
                                kf_propusch_com=kf_propusch_com,
                                kf_wins=kf_wins,
                                kf_zabito_com=kf_zabito_com,
                                mid_propusch_com=mid_propusch_com,
                                mid_zabito_com=mid_zabito_com,
                                not_win_cnt=not_win_cnt,
                                plays=plays,
                                pers_not_wins=pers_not_wins,
                                pers_wins=pers_wins,
                                player_id=player_id,
                                plus_minus=plus_minus if plus_minus is not None else 0,
                                propusch_com=propusch_com,
                                raiting=raiting,
                                standoff_cnt=standoff_cnt,
                                win_cnt=win_cnt,
                                zabito_com=zabito_com,
                                zabito_play=zabito_play,
                            )
                            res.append(raiting.id)

                            if isinstance(division_ids, list):
                                for division_id in division_ids:
                                    Raiting_of_players_division.objects.create(raiting=raiting, division_id=division_id)
                            elif isinstance(tournament_ids, list):
                                for tournament_id in tournament_ids:
                                    Raiting_of_players_tournamet.objects.create(raiting=raiting, tournament_id=tournament_id)
                    if progress.step() != 0:
                        raise ProgressDroped(progress_deleted)
                    # sleep(2)
                    progress.sendInfo('Расчет выполнен')

        return res

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
            'mid_propusch_com': record.mid_propusch_com,
            'mid_zabito_com': record.mid_zabito_com,
            'not_win_cnt': record.not_win_cnt,
            'pays': record.pays,
            'pers_not_wins': record.pers_not_wins,
            'pers_wins': record.pers_wins,
            'player': record.player,
            'plus_minus': record.plus_minus,
            'propusch_com': record.propusch_com,
            'raiting': record.raiting,
            'standoff_cnt': record.standoff_cnt,
            'win_cnt': record.win_cnt,
            'zabito_com': record.zabito_com,
            'zabito_play': record.zabito_play,
        }
        return res

    def get_queryset(self):
        return Raiting_of_playersQuerySet(self.model, using=self._db)


class Raiting_of_players(AuditModel):
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
    player = ForeignKeyProtect(Players)
    plus_minus = DecimalField(max_digits=5, decimal_places=2, )
    propusch_com = DecimalField(max_digits=5, decimal_places=2, )
    raiting = DecimalField(max_digits=5, decimal_places=2, )
    standoff_cnt = DecimalField(verbose_name='Ничьих', max_digits=5, decimal_places=2, )
    win_cnt = DecimalField(max_digits=5, decimal_places=2, )
    zabito_com = DecimalField(max_digits=5, decimal_places=2, )
    zabito_play = DecimalField(max_digits=5, decimal_places=2, )

    objects = Raiting_of_playersManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Рейтинг футболистов'
