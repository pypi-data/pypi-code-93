from isc_common.http.DSResponse import DSResponseUpdate , DSResponseAdd , DSResponse , JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.division_stages import Division_stages , Division_stagesManager


@JsonResponseWithException()
def Division_stages_Fetch( request ) :
    return JsonResponse(
        DSResponse(
            request=request ,
            data=Division_stages.objects.
                select_related().
                get_range_rows1(
                request=request ,
                function=Division_stagesManager.getRecord
            ) ,
            status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Division_stages_Add( request ) :
    return JsonResponse( DSResponseAdd( data=Division_stages.objects.createFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Division_stages_Update( request ) :
    return JsonResponse( DSResponseUpdate( data=Division_stages.objects.updateFromRequest( request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Division_stages_Remove( request ) :
    return JsonResponse( DSResponse( request=request , data=Division_stages.objects.deleteFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Division_stages_Lookup( request ) :
    return JsonResponse( DSResponse( request=request , data=Division_stages.objects.lookupFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Division_stages_Info( request ) :
    return JsonResponse( DSResponse( request=request , data=Division_stages.objects.get_queryset().get_info( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Division_stages_Copy( request ) :
    return JsonResponse( DSResponse( request=request , data=Division_stages.objects.copyFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )
