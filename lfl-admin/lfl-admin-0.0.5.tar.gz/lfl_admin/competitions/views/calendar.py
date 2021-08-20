from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.calendar import Calendar
from lfl_admin.competitions.models.calendar_view import Calendar_view, Calendar_viewManager


@JsonResponseWithException()
def Calendar_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Calendar_view.objects.
                select_related('away', 'away_formation', 'division', 'home', 'home_formation', 'league', 'next_match', 'referee', 'season', 'stadium', 'tournament').
                get_range_rows1(
                request=request,
                function=Calendar_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_Add(request):
    return JsonResponse(DSResponseAdd(data=Calendar.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_Update(request):
    return JsonResponse(DSResponseUpdate(data=Calendar.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Calendar.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Calendar.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_Info(request):
    return JsonResponse(DSResponse(request=request, data=Calendar_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Calendar.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
