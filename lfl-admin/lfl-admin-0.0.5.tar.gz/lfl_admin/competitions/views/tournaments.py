from isc_common.common import unknown
from isc_common.http.DSResponse import DSResponseUpdate , DSResponseAdd , DSResponse , JsonResponseWithException , JsonWSResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.tournaments import Tournaments
from lfl_admin.competitions.models.tournaments_view import Tournaments_view , Tournaments_viewManager


@JsonWSResponseWithException()
def Tournaments_Fetch( request ) :
    return JsonResponse(
        DSResponse(
            request=request ,
            data=Tournaments_view.objects.
                select_related( 'editor' , 'region' , 'season' ).
                exclude( code=unknown ).
                get_range_rows1(
                request=request ,
                function=Tournaments_viewManager.getRecord
            ) ,
            status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_Add( request ) :
    return JsonResponse( DSResponseAdd( data=Tournaments.objects.createFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_Update( request ) :
    return JsonResponse( DSResponseUpdate( data=Tournaments.objects.updateFromRequest( request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_Remove( request ) :
    return JsonResponse( DSResponse( request=request , data=Tournaments.objects.deleteFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_Lookup( request ) :
    return JsonResponse( DSResponse( request=request , data=Tournaments.objects.lookupFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_Info( request ) :
    return JsonResponse( DSResponse( request=request , data=Tournaments_view.objects.get_queryset().get_info( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_Copy( request ) :
    return JsonResponse( DSResponse( request=request , data=Tournaments.objects.copyFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_Add_2_favorites( request ) :
    return JsonResponse( DSResponse( request=request , data=Tournaments_view.objects.get_queryset().add_2_favorites( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_Del_from_favorites( request ) :
    return JsonResponse( DSResponse( request=request , data=Tournaments_view.objects.get_queryset().del_from_favorites( request=request ) , status=RPCResponseConstant.statusSuccess ).response )
