from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.club_logo_history import Club_logo_history, Club_logo_historyManager


@JsonResponseWithException()
def Club_logo_history_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Club_logo_history.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Club_logo_historyManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_logo_history_Add(request):
    return JsonResponse(DSResponseAdd(data=Club_logo_history.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_logo_history_Update(request):
    return JsonResponse(DSResponseUpdate(data=Club_logo_history.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_logo_history_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Club_logo_history.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_logo_history_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Club_logo_history.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_logo_history_Info(request):
    return JsonResponse(DSResponse(request=request, data=Club_logo_history.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_logo_history_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Club_logo_history.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
