import logging

from django.conf import settings
from django.db.models import SmallIntegerField , DateField , BooleanField , F

from isc_common import delAttr , setAttr
from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefHierarcyQuerySet , BaseRefHierarcyManager , BaseRef
from isc_common.number import DelProps
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
from lfl_admin.competitions.models.tournaments import TournamentsManager , Tournaments
from lfl_admin.constructions.models.fields import Fields
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger( __name__ )


class Tournaments_viewQuerySet( BaseRefHierarcyQuerySet ) :
    def prepare_request( self , request ) :
        from lfl_admin.statistic.models.raiting_of_players_tournamet import Raiting_of_players_tournamet

        data = request.get_data()

        ids = data.get( 'ids' )
        if ids is not None :
            tournament_id = list( set( map( lambda x : x.get( 'tournament' ) , Raiting_of_players_tournamet.objects.filter( raiting_id__in=ids ).values( 'tournament' ) ) ) )
            if len( tournament_id ) == 0 :
                tournament_id = [ -1 ]

            delAttr( request.json.get( 'data' ) , 'ids' )
            setAttr( request.json.get( 'data' ) , 'id' , tournament_id )
        return request

    def get_info( self , request , *args ) :
        request = DSRequest( request=request )
        request = self.prepare_request( request )

        criteria = self.get_criteria( json=request.json )
        cnt = super().filter( *args , criteria ).count()
        cnt_all = super().filter().count()
        return dict( qty_rows=cnt , all_rows=cnt_all )

    def add_2_favorites( self , request , *args ) :
        from lfl_admin.competitions.models.tournaments import Tournaments

        request = DSRequest( request=request )
        request = self.prepare_request( request )

        data = request.get_data()
        tournament_ids = data.get( 'tournament_ids' )
        if isinstance( tournament_ids , list ) :
            res = Tournaments.objects.filter( id__in=tournament_ids ).update( props=F( 'props' ).bitor( Tournaments.props.favorites ) )

        return dict( status=RPCResponseConstant.statusSuccess )

    def del_from_favorites( self , request , *args ) :
        from lfl_admin.competitions.models.tournaments import Tournaments

        request = DSRequest( request=request )
        request = self.prepare_request( request )

        data = request.get_data()
        tournament_ids = data.get( 'tournament_ids' )
        if isinstance( tournament_ids , list ) :
            res = Tournaments.objects.filter( id__in=tournament_ids ).update( props=F( 'props' ).bitand( ~Tournaments.props.favorites ) )

        return dict( status=RPCResponseConstant.statusSuccess )

    def get_range_rows1( self , request , function=None , distinct_field_names=None , remove_fields=None ) :
        request = DSRequest( request=request )
        request = self.prepare_request( request )

        data = request.get_data()
        real_id = data.get( 'real_id' )
        if real_id is not None :
            request.set_data( dict( id=real_id ) )

        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
        res = self.get_range_rows(
            start=request.startRow ,
            end=request.endRow ,
            function=function ,
            distinct_field_names=distinct_field_names ,
            json=request.json ,
            criteria=request.get_criteria() ,
            user=request.user
        )
        return res


class Tournaments_viewManager( BaseRefHierarcyManager ) :

    @staticmethod
    def getRecord( record ) :
        scheme_real_name , scheme_image_src = Tournaments.get_urls_data( id=record.id , code='scheme' )
        logo_real_name , logo_image_src = Tournaments.get_urls_data( id=record.id , code='logo' )

        res = {
            'active' : record.active ,
            'code' : record.code ,
            'condition__name' : record.disqualification_condition.name ,
            'condition_id' : record.disqualification_condition.id ,
            'deliting' : record.deliting ,
            'description' : record.description ,
            'division__name' : record.division.name ,
            'division_id' : record.division.id ,
            'division_priority' : record.division_priority ,
            'division_round' : record.division_round ,
            'down2_selected' : record.down2_selected ,
            'down_selected' : record.down_selected ,
            'editing' : record.editing ,
            'editor_id' : record.editor.id if record.editor else None ,
            'editor_short_name' : record.editor.get_short_name if record.editor else None ,
            'favorites' : record.favorites ,
            'field__name' : record.field.name ,
            'field_id' : record.field.id ,
            'hidden' : record.hidden ,
            'id' : record.id ,
            'league__name' : record.league.name ,
            'league_id' : record.league.id ,
            'logo_image_src' : logo_image_src ,
            'logo_real_name' : logo_real_name ,
            'logo_real_name' : record.logo_real_name ,
            'logo_src' : f'http://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.logo_image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}' ,
            'loss_points_rule' : record.loss_points_rule ,
            'name' : record.name ,
            'national' : record.national ,
            'number_of_players' : record.number_of_players ,
            'number_of_rounds' : record.number_of_rounds ,
            'number_of_teams' : record.number_of_teams ,
            'number_of_tours' : record.number_of_tours ,
            'priority' : record.priority ,
            'props' : record.props ,
            'protocol_type__name' : record.protocol_type.name ,
            'protocol_type_id' : record.protocol_type.id ,
            'rating_rule__name' : record.rating_rule.name if record.rating_rule else None ,
            'rating_rule_id' : record.rating_rule.id if record.rating_rule else None ,
            'referee_category__name' : record.referee_category.name ,
            'referee_category_id' : record.referee_category.id ,
            'referees_max' : record.referees_max ,
            'region__name' : record.region.name ,
            'region_id' : record.region.id ,
            'round' : record.round ,
            'scheme_image_src' : scheme_image_src ,
            'scheme_real_name' : scheme_real_name ,
            'season__name' : record.season.name ,
            'season_id' : record.season.id ,
            'show_empty_cells' : record.show_empty_cells ,
            'show_league' : record.show_league ,
            'show_numbers' : record.show_numbers ,
            'show_player_number' : record.show_player_number ,
            'show_region' : record.show_region ,
            'show_stats' : record.show_stats ,
            'start_date' : record.start_date ,
            'statistics_type__name' : record.statistics_type.name ,
            'statistics_type_id' : record.statistics_type.id ,
            'technical_defeat__name' : record.technical_defeat.name ,
            'technical_defeat_id' : record.technical_defeat.id ,
            'tournament_type__name' : record.tournament_type.name ,
            'tournament_type_id' : record.tournament_type.id ,
            'up2_selected' : record.up2_selected ,
            'up_selected' : record.up_selected ,
            'zone__name' : record.zone.name ,
            'zone_id' : record.zone.id ,
        }
        return DelProps( res )

    def get_queryset( self ) :
        return Tournaments_viewQuerySet( self.model , using=self._db )


class Tournaments_view( BaseRef , Model_withOldId ) :
    active = BooleanField()
    code = CodeField()
    disqualification_condition = ForeignKeyProtect( Disqualification_condition )
    division = ForeignKeyProtect( Divisions )
    division_priority = SmallIntegerField()
    division_round = SmallIntegerField( null=True , blank=True )
    down2_selected = SmallIntegerField( null=True , blank=True )
    down_selected = SmallIntegerField( null=True , blank=True )
    editor = ForeignKeyProtect( User , null=True , blank=True )
    favorites = BooleanField()
    field = ForeignKeyProtect( Fields )
    hidden = BooleanField()
    league = ForeignKeyProtect( Leagues )
    logo_image_src = NameField()
    logo_real_name = NameField()
    loss_points_rule = BooleanField()
    national = BooleanField()
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
    show_empty_cells = BooleanField()
    show_league = BooleanField()
    show_numbers = BooleanField()
    show_player_number = BooleanField()
    show_region = BooleanField()
    show_stats = BooleanField()
    start_date = DateField( null=True , blank=True )
    statistics_type = ForeignKeyProtect( Statistics_types )
    technical_defeat = ForeignKeyProtect( Technical_defeat )
    tournament_type = ForeignKeyProtect( Tournament_types )
    up2_selected = SmallIntegerField( null=True , blank=True )
    up_selected = SmallIntegerField( null=True , blank=True )
    zone = ForeignKeyProtect( Disqualification_zones )

    objects = Tournaments_viewManager()

    def __str__( self ) :
        return f'ID:{self.id}'

    def __repr__( self ) :
        return self.__str__()

    class Meta :
        verbose_name = 'Турниры'
        db_table = 'competitions_tournaments_view'
        managed = False
