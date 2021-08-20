import logging

from django.db.models import SmallIntegerField, DateTimeField, BooleanField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import Model_withOldId, AuditManager, AuditQuerySet, AuditModel
from isc_common.number import DelProps
from lfl_admin.competitions.models.calendar import CalendarManager, Calendar
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.divisions import Divisions
from lfl_admin.competitions.models.formation import Formation
from lfl_admin.competitions.models.leagues import Leagues
from lfl_admin.competitions.models.referees import Referees
from lfl_admin.competitions.models.seasons import Seasons
from lfl_admin.competitions.models.tournaments import Tournaments
from lfl_admin.constructions.models.stadiums import Stadiums

logger = logging.getLogger(__name__)


class Calendar_viewQuerySet(AuditQuerySet):
    def prepare_request(self, request):
        data = request.get_data()

        division_ids = data.get('division_ids')
        if division_ids is None:
            tounament_ids = data.get('tournaments_ids')
        else:
            tounament_ids = list(set(map(lambda x: x.get('id'), Tournaments.objects.filter(division_id__in=division_ids, props=Tournaments.props.active).values('id'))))

        if tounament_ids is not None:
            ids = list(set(map(lambda x: x.get('id'), Calendar.objects.filter(tournament_id__in=tounament_ids).values('id'))))
            if len(ids) == 0:
                ids = [-1]

            request.set_data(dict(id=ids))
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


class Calendar_viewManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'away__name': record.away.name,
            'away_id': record.away.id,
            'away_points': record.away_points,
            'away_score': record.away_score,
            'checked': record.checked,
            'deliting': record.deliting,
            'division__name': record.division.name,
            'division_id': record.division.id,
            'editing': record.editing,
            'home__name': record.home.name,
            'home_formation__name': record.home_formation.name,
            'home_formation_id': record.home_formation.id,
            'home_id': record.home.id,
            'home_points': record.home_points,
            'home_score': record.home_score,
            'id': record.id,
            'league__name': record.league.name,
            'league_id': record.league.id,
            'match_date_time': record.match_date_time,
            'match_number': record.match_number,
            'next_match_id': record.next_match.id if record.next_match is not None else None,
            'props': record.props,
            'referee__name': record.referee.person.user.get_short_name,
            'referee_id': record.referee.id,
            'score': record.score,
            'season__name': record.season.name,
            'season_id': record.season.id,
            'stadium__name': record.stadium.name,
            'stadium_id': record.stadium.id,
            'technical_defeat': record.technical_defeat,
            'tour': record.tour,
            'tour_title': record.tour_title,
            'tournament__name': record.tournament.name,
            'tournament_id': record.tournament.id,
        }
        return DelProps(res)

    def get_queryset(self):
        return Calendar_viewQuerySet(self.model, using=self._db)


class Calendar_view(AuditModel, Model_withOldId):
    away = ForeignKeyProtect(Clubs, related_name='Calendar_view_away')
    away_formation = ForeignKeyProtect(Formation, related_name='Calendar_view_away_formation')
    away_points = SmallIntegerField()
    away_score = SmallIntegerField()
    checked = SmallIntegerField(default=0)
    division = ForeignKeyProtect(Divisions)
    editor = ForeignKeyProtect(User, null=True, blank=True)
    home = ForeignKeyProtect(Clubs, related_name='Calendar_view_home')
    home_formation = ForeignKeyProtect(Formation, related_name='Calendar_view_home_formation')
    home_points = SmallIntegerField()
    home_score = SmallIntegerField()
    league = ForeignKeyProtect(Leagues)
    match_date_time = DateTimeField(null=True, blank=True)
    match_number = SmallIntegerField()
    next_match = ForeignKeyProtect('self', null=True, blank=True)
    props = CalendarManager.props()
    referee = ForeignKeyProtect(Referees)
    score = CodeField()
    season = ForeignKeyProtect(Seasons)
    stadium = ForeignKeyProtect(Stadiums)
    technical_defeat = SmallIntegerField()
    tour = SmallIntegerField()
    tour_title = NameField()
    tournament = ForeignKeyProtect(Tournaments)

    objects = Calendar_viewManager()

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
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Календарь матчей турнира'
        db_table = 'competitions_calendar_view'
        managed = False
