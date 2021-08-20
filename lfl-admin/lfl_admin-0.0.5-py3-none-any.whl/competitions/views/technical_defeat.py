from isc_common.http.DSResponse import DSResponseUpdate , DSResponseAdd , DSResponse , JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.technical_defeat import Technical_defeat , Technical_defeatManager


@JsonResponseWithException()
def Technical_defeat_Fetch( request ) :
    return JsonResponse(
        DSResponse(
            request=request ,
            data=Technical_defeat.objects.
                filter().
                get_range_rows1(
                request=request ,
                function=Technical_defeatManager.getRecord
            ) ,
            status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Technical_defeat_Add( request ) :
    return JsonResponse( DSResponseAdd( data=Technical_defeat.objects.createFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Technical_defeat_Update( request ) :
    return JsonResponse( DSResponseUpdate( data=Technical_defeat.objects.updateFromRequest( request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Technical_defeat_Remove( request ) :
    return JsonResponse( DSResponse( request=request , data=Technical_defeat.objects.deleteFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Technical_defeat_Lookup( request ) :
    return JsonResponse( DSResponse( request=request , data=Technical_defeat.objects.lookupFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Technical_defeat_Info( request ) :
    return JsonResponse( DSResponse( request=request , data=Technical_defeat.objects.get_queryset().get_info( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Technical_defeat_Copy( request ) :
    return JsonResponse( DSResponse( request=request , data=Technical_defeat.objects.copyFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )
