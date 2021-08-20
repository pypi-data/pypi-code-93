from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.club_histories import Club_histories, Club_historiesManager


@JsonResponseWithException()
def Club_histories_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Club_histories.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Club_historiesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_histories_Add(request):
    return JsonResponse(DSResponseAdd(data=Club_histories.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_histories_Update(request):
    return JsonResponse(DSResponseUpdate(data=Club_histories.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_histories_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Club_histories.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_histories_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Club_histories.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_histories_Info(request):
    return JsonResponse(DSResponse(request=request, data=Club_histories.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_histories_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Club_histories.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
