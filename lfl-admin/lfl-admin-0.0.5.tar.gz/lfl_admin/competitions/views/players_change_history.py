from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.players_change_history import Players_change_history, Players_change_historyManager


@JsonResponseWithException()
def Players_change_history_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Players_change_history.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Players_change_historyManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_change_history_Add(request):
    return JsonResponse(DSResponseAdd(data=Players_change_history.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_change_history_Update(request):
    return JsonResponse(DSResponseUpdate(data=Players_change_history.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_change_history_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Players_change_history.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_change_history_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Players_change_history.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_change_history_Info(request):
    return JsonResponse(DSResponse(request=request, data=Players_change_history.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_change_history_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Players_change_history.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
