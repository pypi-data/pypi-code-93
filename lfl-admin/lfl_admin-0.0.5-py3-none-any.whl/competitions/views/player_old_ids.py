from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.player_old_ids import Player_old_ids, Player_old_idsManager


@JsonResponseWithException()
def Player_old_ids_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Player_old_ids.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Player_old_idsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_old_ids_Add(request):
    return JsonResponse(DSResponseAdd(data=Player_old_ids.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_old_ids_Update(request):
    return JsonResponse(DSResponseUpdate(data=Player_old_ids.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_old_ids_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Player_old_ids.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_old_ids_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Player_old_ids.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_old_ids_Info(request):
    return JsonResponse(DSResponse(request=request, data=Player_old_ids.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_old_ids_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Player_old_ids.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
