from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.statistic.models.raiting_of_players import Raiting_of_players
from lfl_admin.statistic.models.raiting_of_players_view import Raiting_of_players_view, Raiting_of_players_viewManager


@JsonResponseWithException()
def Raiting_of_players_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Raiting_of_players_view.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Raiting_of_players_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_Add(request):
    return JsonResponse(DSResponseAdd(data=Raiting_of_players.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_Update(request):
    return JsonResponse(DSResponseUpdate(data=Raiting_of_players.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_CalcStatic(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players.objects.calcStaticFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_Info(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
