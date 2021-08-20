from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.match_stats import Match_stats, Match_statsManager


@JsonResponseWithException()
def Match_stats_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Match_stats.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Match_statsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_stats_Add(request):
    return JsonResponse(DSResponseAdd(data=Match_stats.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_stats_Update(request):
    return JsonResponse(DSResponseUpdate(data=Match_stats.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_stats_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Match_stats.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_stats_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Match_stats.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_stats_Info(request):
    return JsonResponse(DSResponse(request=request, data=Match_stats.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_stats_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Match_stats.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
