from django.utils.translation import ugettext_lazy as _

import logging

from isc_common.models.base_ref import BaseRefManager , BaseRefQuerySet , BaseRef

logger = logging.getLogger( __name__ )


class Technical_defeatQuerySet( BaseRefQuerySet ) :
    pass


class Technical_defeatManager( BaseRefManager ) :

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
        return Technical_defeatQuerySet( self.model , using=self._db )


class Technical_defeat( BaseRef ) :
    objects = Technical_defeatManager()

    def __str__( self ) :
        return f'ID:{self.id}'

    def __repr__( self ) :
        return self.__str__()

    class Meta :
        verbose_name = 'Тип технического поражения'
