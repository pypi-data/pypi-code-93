from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.player_histories import Player_histories, Player_historiesManager


@JsonResponseWithException()
def Player_histories_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Player_histories.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Player_historiesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_histories_Add(request):
    return JsonResponse(DSResponseAdd(data=Player_histories.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_histories_Update(request):
    return JsonResponse(DSResponseUpdate(data=Player_histories.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_histories_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Player_histories.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_histories_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Player_histories.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_histories_Info(request):
    return JsonResponse(DSResponse(request=request, data=Player_histories.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_histories_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Player_histories.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
