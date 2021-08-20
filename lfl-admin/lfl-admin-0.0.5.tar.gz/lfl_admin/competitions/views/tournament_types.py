from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.tournament_types import Tournament_types, Tournament_typesManager


@JsonResponseWithException()
def Tournament_types_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Tournament_types.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Tournament_typesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_types_Add(request):
    return JsonResponse(DSResponseAdd(data=Tournament_types.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_types_Update(request):
    return JsonResponse(DSResponseUpdate(data=Tournament_types.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_types_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_types.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_types_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_types.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_types_Info(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_types.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_types_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_types.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
