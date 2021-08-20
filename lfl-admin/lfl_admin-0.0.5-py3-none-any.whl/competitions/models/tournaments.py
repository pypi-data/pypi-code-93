import logging

from bitfield import BitField
from django.db import transaction , connection
from django.db.models import SmallIntegerField , DateField

from isc_common.auth.models.user import User
from isc_common.common import unknown
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefHierarcyQuerySet , BaseRefHierarcyManager , BaseRef
from lfl_admin.competitions.models.disqualification_condition import Disqualification_condition
from lfl_admin.competitions.models.disqualification_zones import Disqualification_zones
from lfl_admin.competitions.models.divisions import Divisions
from lfl_admin.competitions.models.leagues import Leagues
from lfl_admin.competitions.models.protocol_types import Protocol_types
from lfl_admin.competitions.models.rating_rule import Rating_rule
from lfl_admin.competitions.models.referee_category import Referee_category
from lfl_admin.competitions.models.seasons import Seasons
from lfl_admin.competitions.models.statistics_types import Statistics_types
from lfl_admin.competitions.models.technical_defeat import Technical_defeat
from lfl_admin.competitions.models.tournament_types import Tournament_types
from lfl_admin.constructions.models.fields import Fields
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger( __name__ )


class TournamentsQuerySet( BaseRefHierarcyQuerySet ) :
    pass


class TournamentsManager( BaseRefHierarcyManager ) :
    def updateFromRequest( self , request , removed=None , function=None ) :
        request = DSRequest( request=request )
        data = request.get_data()
        id = data.get( 'id' )
        props = data.get( 'props' )

        favorites = data.get( 'favorites' )
        if favorites is True :
            props |= Tournaments.props.favorites
        else :
            props &= ~Tournaments.props.favorites

        hidden = data.get( 'hidden' )
        if hidden is True :
            props |= Tournaments.props.hidden
        else :
            props &= ~Tournaments.props.hidden

        with transaction.atomic() :
            super().filter( id=id ).update( props=props )
        return data

    @classmethod
    def props( cls ) :
        return BitField( flags=(
            ('active' , 'active') ,  # 0
            ('national' , 'national') ,  # 1
            ('show_league' , 'show_league') ,  # 2
            ('show_region' , 'show_region') ,  # 3
            ('unused' , 'up_selected') ,  # 4
            ('unused1' , 'up2_selected') ,  # 5
            ('unused2' , 'down_selected') ,  # 6
            ('unused3' , 'down2_selected') ,  # 7
            ('calendar_created' , 'calendar_created') ,  # 8
            ('show_numbers' , 'show_numbers') ,  # 9
            ('show_player_number' , 'show_player_number') ,  # 10
            ('show_stats' , 'show_stats') ,  # 11
            ('show_empty_cells' , 'show_empty_cells') ,  # 12
            ('favorites' , 'Избранные') ,  # 13
            ('hidden' , 'Скрывать ФИО') ,  # 14
            ('loss_points_rule' , 'Подключить расстановку команд в текущей (не итоговой таблице), в случае равенства очков, по потерянным очкам') ,  # 15
        ) , default=1 , db_index=True )

    @staticmethod
    def getRecord( record ) :
        res = {
            'id' : record.id ,
            'code' : record.code ,
            'name' : record.name ,
            'description' : record.description ,
            'editing' : record.editing ,
            'deliting' : record.deliting ,
        }
        return res

    def get_queryset( self ) :
        return TournamentsQuerySet( self.model , using=self._db )


class Tournaments( BaseRef , Model_withOldId ) :
    code = CodeField()
    disqualification_condition = ForeignKeyProtect( Disqualification_condition )
    division = ForeignKeyProtect( Divisions )
    division_priority = SmallIntegerField()
    division_round = SmallIntegerField( null=True , blank=True )
    down2_selected = SmallIntegerField( null=True , blank=True )
    down_selected = SmallIntegerField( null=True , blank=True )
    editor = ForeignKeyProtect( User , null=True , blank=True )
    field = ForeignKeyProtect( Fields )
    league = ForeignKeyProtect( Leagues )
    number_of_players = SmallIntegerField()
    number_of_rounds = SmallIntegerField()
    number_of_teams = SmallIntegerField()
    number_of_tours = SmallIntegerField()
    priority = SmallIntegerField()
    props = TournamentsManager.props()
    protocol_type = ForeignKeyProtect( Protocol_types )
    rating_rule = ForeignKeyProtect( Rating_rule )
    referee_category = ForeignKeyProtect( Referee_category )
    referees_max = SmallIntegerField()
    region = ForeignKeyProtect( Regions )
    round = SmallIntegerField( null=True , blank=True )
    season = ForeignKeyProtect( Seasons )
    start_date = DateField( null=True , blank=True )
    statistics_type = ForeignKeyProtect( Statistics_types )
    technical_defeat = ForeignKeyProtect( Technical_defeat )
    tournament_type = ForeignKeyProtect( Tournament_types )
    up2_selected = SmallIntegerField( null=True , blank=True )
    up_selected = SmallIntegerField( null=True , blank=True )
    zone = ForeignKeyProtect( Disqualification_zones )

    objects = TournamentsManager()

    @classmethod
    def get_urls_data( cls , id , code ) :
        with connection.cursor() as cursor :
            cursor.execute( f'''select (select ici.real_name
                                        from competitions_tournaments_images as usi
                                                 join isc_common_images ici on ici.id = usi.image_id
                                                 join isc_common_image_types icit on ici.image_type_id = icit.id
                                        where usi.main_model_id = cd.id
                                          and icit.code = %s
                                        limit 1)                                                                                                           as real_name,
                                       concat('logic/Imgs/Download/', (
                                           select usi.image_id
                                           from competitions_tournaments_images as usi
                                                    join isc_common_images ici on ici.id = usi.image_id
                                                    join isc_common_image_types icit on ici.image_type_id = icit.id
                                           where usi.main_model_id = cd.id
                                             and icit.code = %s
                                           limit 1), '?', 'code={code}', '&', 'path=tournaments', '&', 'main_model=tournaments', '&', 'main_model_id=', cd.id) as image_src
                                from competitions_tournaments as cd
                                where cd.id = %s''' , [ code, code,id ] )
            record = cursor.fetchone()
            return record

    @classmethod
    def unknown( cls ) :
        res , _ = cls.objects.get_or_create(
            code=unknown ,
            disqualification_condition=0 ,
            division=Divisions.unknown() ,
            division_priority=0 ,
            field=Fields.unknown() ,
            league=Leagues.unknown() ,
            number_of_players=0 ,
            number_of_rounds=0 ,
            number_of_teams=0 ,
            number_of_tours=0 ,
            priority=0 ,
            protocol_type=Protocol_types.unknown() ,
            rating_rule=0 ,
            referee_category=Referee_category.unknown() ,
            referees_max=0 ,
            region=Regions.unknown() ,
            season=Seasons.unknown() ,
            statistics_type=Statistics_types.unknown() ,
            tournament_type=Tournament_types.unknown() ,
            zone=Disqualification_zones.unknown()
        )
        return res

    def __str__( self ) :
        return f'ID:{self.id}'

    def __repr__( self ) :
        return self.__str__()

    class Meta :
        verbose_name = 'Турниры'
