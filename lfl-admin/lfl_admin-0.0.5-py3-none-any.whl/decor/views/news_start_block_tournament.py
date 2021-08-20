from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.decor.models.news_start_block_tournament import News_start_block_tournament, News_start_block_tournamentManager


@JsonResponseWithException()
def News_start_block_tournament_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=News_start_block_tournament.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=News_start_block_tournamentManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_start_block_tournament_Add(request):
    return JsonResponse(DSResponseAdd(data=News_start_block_tournament.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_start_block_tournament_Update(request):
    return JsonResponse(DSResponseUpdate(data=News_start_block_tournament.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_start_block_tournament_Remove(request):
    return JsonResponse(DSResponse(request=request, data=News_start_block_tournament.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_start_block_tournament_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=News_start_block_tournament.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_start_block_tournament_Info(request):
    return JsonResponse(DSResponse(request=request, data=News_start_block_tournament.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_start_block_tournament_Copy(request):
    return JsonResponse(DSResponse(request=request, data=News_start_block_tournament.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
