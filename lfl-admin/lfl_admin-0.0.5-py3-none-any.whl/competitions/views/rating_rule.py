from isc_common.http.DSResponse import DSResponseUpdate , DSResponseAdd , DSResponse , JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.rating_rule import Rating_rule , Rating_ruleManager


@JsonResponseWithException()
def Rating_rule_Fetch( request ) :
    return JsonResponse(
        DSResponse(
            request=request ,
            data=Rating_rule.objects.
                select_related().
                get_range_rows1(
                request=request ,
                function=Rating_ruleManager.getRecord
            ) ,
            status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Rating_rule_Add( request ) :
    return JsonResponse( DSResponseAdd( data=Rating_rule.objects.createFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Rating_rule_Update( request ) :
    return JsonResponse( DSResponseUpdate( data=Rating_rule.objects.updateFromRequest( request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Rating_rule_Remove( request ) :
    return JsonResponse( DSResponse( request=request , data=Rating_rule.objects.deleteFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Rating_rule_Lookup( request ) :
    return JsonResponse( DSResponse( request=request , data=Rating_rule.objects.lookupFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Rating_rule_Info( request ) :
    return JsonResponse( DSResponse( request=request , data=Rating_rule.objects.get_queryset().get_info( request=request ) , status=RPCResponseConstant.statusSuccess ).response )


@JsonResponseWithException()
def Rating_rule_Copy( request ) :
    return JsonResponse( DSResponse( request=request , data=Rating_rule.objects.copyFromRequest( request=request ) , status=RPCResponseConstant.statusSuccess ).response )
