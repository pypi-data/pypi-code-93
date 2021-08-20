from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.protocol_types import Protocol_types, Protocol_typesManager


@JsonResponseWithException()
def Protocol_types_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Protocol_types.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Protocol_typesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Protocol_types_Add(request):
    return JsonResponse(DSResponseAdd(data=Protocol_types.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Protocol_types_Update(request):
    return JsonResponse(DSResponseUpdate(data=Protocol_types.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Protocol_types_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Protocol_types.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Protocol_types_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Protocol_types.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Protocol_types_Info(request):
    return JsonResponse(DSResponse(request=request, data=Protocol_types.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Protocol_types_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Protocol_types.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
