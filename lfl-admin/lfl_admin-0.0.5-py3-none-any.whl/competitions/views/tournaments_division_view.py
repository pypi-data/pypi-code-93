from isc_common.http.DSResponse import DSResponseUpdate , DSResponseAdd , DSResponse , JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.tournaments_division_view import Tournaments_division_view , Tournaments_division_viewManager


@JsonResponseWithException()
def Tournaments_division_view_Fetch( request ) :
    return JsonResponse(
        DSResponse(
            request=request ,
            data=Tournaments_division_view.objects.
                select_related( 'editor' , 'region' , 'season' , 'tournament_type' ).
                get_range_rows1(
                request=request ,
                function=Tournaments_division_viewManager.getRecord
            ) ,
            status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_division_view_Add( request ) :
    return JsonResponse( DSResponseAdd( data=Tournaments_division_view.objects.createFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_division_view_Update( request ) :
    return JsonResponse( DSResponseUpdate( data=Tournaments_division_view.objects.updateFromRequest( request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_division_view_Remove( request ) :
    return JsonResponse( DSResponse( request=request , data=Tournaments_division_view.objects.deleteFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_division_view_Lookup( request ) :
    return JsonResponse( DSResponse( request=request , data=Tournaments_division_view.objects.lookupFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_division_view_Info( request ) :
    return JsonResponse( DSResponse( request=request , data=Tournaments_division_view.objects.get_queryset().get_info( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Tournaments_division_view_Copy( request ) :
    return JsonResponse( DSResponse( request=request , data=Tournaments_division_view.objects.copyFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )
