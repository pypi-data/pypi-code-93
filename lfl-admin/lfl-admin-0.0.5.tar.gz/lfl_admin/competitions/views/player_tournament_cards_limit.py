from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.player_tournament_cards_limit import Player_tournament_cards_limit, Player_tournament_cards_limitManager


@JsonResponseWithException()
def Player_tournament_cards_limit_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Player_tournament_cards_limit.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Player_tournament_cards_limitManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_tournament_cards_limit_Add(request):
    return JsonResponse(DSResponseAdd(data=Player_tournament_cards_limit.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_tournament_cards_limit_Update(request):
    return JsonResponse(DSResponseUpdate(data=Player_tournament_cards_limit.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_tournament_cards_limit_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Player_tournament_cards_limit.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_tournament_cards_limit_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Player_tournament_cards_limit.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_tournament_cards_limit_Info(request):
    return JsonResponse(DSResponse(request=request, data=Player_tournament_cards_limit.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Player_tournament_cards_limit_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Player_tournament_cards_limit.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
