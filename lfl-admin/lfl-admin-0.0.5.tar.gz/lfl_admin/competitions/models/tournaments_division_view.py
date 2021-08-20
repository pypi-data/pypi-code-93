import logging

from django.db.models import SmallIntegerField , BooleanField , BigIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefHierarcyQuerySet , BaseRefHierarcyManager , BaseRefHierarcy
from isc_common.number import DelProps
from lfl_admin.competitions.models.leagues import Leagues
from lfl_admin.competitions.models.seasons import Seasons
from lfl_admin.competitions.models.tournament_types import Tournament_types
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger( __name__ )


class Tournaments_division_viewQuerySet( BaseRefHierarcyQuerySet ) :
    pass


class Tournaments_division_viewManager( BaseRefHierarcyManager ) :

    @staticmethod
    def getRecord( record ) :
        res = {
            'active' : record.active ,
            'deliting' : record.deliting ,
            'editing' : record.editing ,
            'editor_id' : record.editor.id if record.editor else None ,
            'editor_short_name' : record.editor.get_short_name if record.editor else None ,
            'favorites' : record.favorites ,
            'hidden' : record.hidden ,
            'id' : record.id ,
            'is_division' : record.is_division ,
            'isFolder' : record.is_division ,
            'league__name' : record.league.name if record.league else None ,
            'league_id' : record.league.id if record.league else None ,
            'name' : record.name ,
            'number_of_rounds' : record.number_of_rounds ,
            'number_of_teams' : record.number_of_teams ,
            'old_id' : record.old_id ,
            'priority' : record.priority ,
            'real_id' : record.real_id ,
            'region__name' : record.region.name ,
            'region_id' : record.region.id ,
            'season__name' : record.season.name if record.season else None ,
            'season_id' : record.season.id if record.season else None ,
            'tournament_type__name' : record.tournament_type.name if record.tournament_type else None ,
            'tournament_type_id' : record.tournament_type.id if record.tournament_type else None ,
        }
        return DelProps( res )

    def get_queryset( self ) :
        return Tournaments_division_viewQuerySet( self.model , using=self._db )


class Tournaments_division_view( BaseRefHierarcy , Model_withOldId ) :
    active = BooleanField()
    editor = ForeignKeyProtect( User , null=True , blank=True )
    favorites = BooleanField()
    hidden = BooleanField()
    is_division = BooleanField()
    isFolder = BooleanField()
    name = CodeField()
    number_of_rounds = SmallIntegerField()
    league = ForeignKeyProtect( Leagues, null=True , blank=True )
    number_of_teams = SmallIntegerField( null=True , blank=True )
    priority = SmallIntegerField( null=True , blank=True )
    real_id = BigIntegerField( db_index=True )
    region = ForeignKeyProtect( Regions )
    season = ForeignKeyProtect( Seasons , null=True , blank=True )
    tournament_type = ForeignKeyProtect( Tournament_types , null=True , blank=True )

    objects = Tournaments_division_viewManager()

    def __str__( self ) :
        return f'ID:{self.id}'

    def __repr__( self ) :
        return self.__str__()

    class Meta :
        verbose_name = 'Турниры объединенные с супе турнирами'
        db_table = 'competitions_tournaments_division_view'
        managed = False
