import logging

from bitfield import BitField
from django.db.models import SmallIntegerField, DateTimeField

from isc_common import setAttr, delAttr
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import Model_withOldId, AuditManager, AuditQuerySet, AuditModel
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.divisions import Divisions
from lfl_admin.competitions.models.formation import Formation
from lfl_admin.competitions.models.leagues import Leagues
from lfl_admin.competitions.models.referees import Referees
from lfl_admin.competitions.models.seasons import Seasons
from lfl_admin.competitions.models.tournaments import Tournaments
from lfl_admin.constructions.models.stadiums import Stadiums

logger = logging.getLogger(__name__)


class CalendarQuerySet(AuditQuerySet):
    pass


class CalendarManager(AuditManager):
    def updateFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()

        id = data.get('id')
        res = dict()

        delAttr(res, 'score')
        setAttr(res, 'away_id', data.get('away_id'))
        setAttr(res, 'away_points', data.get('away_points'))
        setAttr(res, 'away_score', data.get('away_score'))
        setAttr(res, 'division_id', data.get('division_id'))
        setAttr(res, 'home_formation_id', data.get('home_formation_id'))
        setAttr(res, 'home_id', data.get('home_id'))
        setAttr(res, 'home_points', data.get('home_points'))
        setAttr(res, 'home_score', data.get('home_score'))

        setAttr(res, 'league_id', data.get('league_id'))
        setAttr(res, 'match_date_time', data.get('match_date_time'))
        setAttr(res, 'match_number', data.get('match_number'))
        setAttr(res, 'props', data.get('props'))
        setAttr(res, 'referee_id', data.get('referee_id'))
        setAttr(res, 'season_id', data.get('season_id'))
        setAttr(res, 'stadium_id', data.get('stadium_id'))
        setAttr(res, 'technical_defeat', data.get('technical_defeat'))
        setAttr(res, 'tour', data.get('tour'))
        setAttr(res, 'tournament_id', data.get('tournament_id'))

        # with transaction.atomic():
        #     Calendar.objects.filter(id=id).update(**res)
        #
        #     for command_structure in Command_structure_tmp.objects.filter(editor=request.user):
        #         if command_structure.player_histories is None:
        #             Player_histories.objects.create(
        #                 club=command_structure.club,
        #                 editor=request.user,
        #                 formation=command_structure.formation,
        #                 match=command_structure.match,
        #                 num=command_structure.num,
        #                 player=command_structure.player,
        #                 props=command_structure.match.props,
        #                 tournament=command_structure.tournament
        #             )
        #         else:
        #             Player_histories.objects.filter(id=command_structure.player_histories.id).update(
        #                 club=command_structure.club,
        #                 editor=request.user,
        #                 formation=command_structure.formation,
        #                 match=command_structure.match,
        #                 num=command_structure.num,
        #                 player=command_structure.player,
        #                 props=command_structure.match.props,
        #                 tournament=command_structure.tournament
        #             )
        #
        #     player_histories_query = Player_histories.objects.filter(match_id=id).exclude(id__in=map(lambda x: x.player_histories.id, Command_structure_tmp.objects.filter(editor=request.user)))
        #     player_histories_query.soft_delete()

        return data

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('protocol', 'protocol'),  # 1
            ('in_archive', 'in_archive'),  # 1
            ('show_stats', 'show_stats'),  # 1
            ('show_empty_cells', 'show_empty_cells'),  # 1
            ('penalty', 'penalty'),  # 1
        ), default=0, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return CalendarQuerySet(self.model, using=self._db)


class Calendar(AuditModel, Model_withOldId):
    away = ForeignKeyProtect(Clubs, related_name='Calendar_away')
    away_formation = ForeignKeyProtect(Formation, related_name='Calendar_away_formation')
    away_points = SmallIntegerField()
    away_score = SmallIntegerField()
    checked = SmallIntegerField(default=0)
    division = ForeignKeyProtect(Divisions)
    editor = ForeignKeyProtect(User, null=True, blank=True)
    home = ForeignKeyProtect(Clubs, related_name='Calendar_home')
    home_formation = ForeignKeyProtect(Formation, related_name='Calendar_home_formation')
    home_points = SmallIntegerField()
    home_score = SmallIntegerField()
    league = ForeignKeyProtect(Leagues)
    match_date_time = DateTimeField(null=True, blank=True)
    match_number = SmallIntegerField()
    next_match = ForeignKeyProtect('self', null=True, blank=True)
    props = CalendarManager.props()
    referee = ForeignKeyProtect(Referees)
    season = ForeignKeyProtect(Seasons)
    stadium = ForeignKeyProtect(Stadiums)
    technical_defeat = SmallIntegerField()
    tour = SmallIntegerField()
    tournament = ForeignKeyProtect(Tournaments)

    objects = CalendarManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            away=Clubs.unknown(),
            away_formation=Formation.unknown(),
            away_points=0,
            away_score=0,
            checked=0,
            home=Clubs.unknown(),
            division=Divisions.unknown(),
            home_formation=Formation.unknown(),
            home_points=0,
            home_score=0,
            league=Leagues.unknown(),
            match_number=0,
            referee=Referees.unknown(),
            season=Seasons.unknown(),
            stadium=Stadiums.unknown(),
            technical_defeat=0,
            tour=0,
            tournament=Tournaments.unknown()
        )
        return res

    def __str__(self):
        return f'ID:{self.id} away: [{self.away}] home: [{self.home}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Календарь матчей турнира'
