from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.statistic.models.raiting_of_players_tournamet import Raiting_of_players_tournamet, Raiting_of_players_tournametManager


@JsonResponseWithException()
def Raiting_of_players_tournamet_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Raiting_of_players_tournamet.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Raiting_of_players_tournametManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_tournamet_Add(request):
    return JsonResponse(DSResponseAdd(data=Raiting_of_players_tournamet.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_tournamet_Update(request):
    return JsonResponse(DSResponseUpdate(data=Raiting_of_players_tournamet.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_tournamet_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players_tournamet.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_tournamet_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players_tournamet.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_tournamet_Info(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players_tournamet.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Raiting_of_players_tournamet_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Raiting_of_players_tournamet.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
