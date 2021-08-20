from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.statistic.models.raiting_of_players_division import Raiting_of_players_divisionManager, Raiting_of_players_division


@JsonResponseWithException()
def Raiting_of_players_division_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Raiting_of_players_division.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Raiting_of_players_divisionManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_division_Add(request):
    return JsonResponse(DSResponseAdd(data=Raiting_of_players_division.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_division_Update(request):
    return JsonResponse(DSResponseUpdate(data=Raiting_of_players_division.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_division_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players_division.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_division_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players_division.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_division_Info(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players_division.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_division_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players_division.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
