from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.seasons import Seasons, SeasonsManager


@JsonResponseWithException()
def Seasons_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Seasons.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=SeasonsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Seasons_Add(request):
    return JsonResponse(DSResponseAdd(data=Seasons.objects.createFromRequest(request=request, propsArr=['active']), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Seasons_Update(request):
    return JsonResponse(DSResponseUpdate(data=Seasons.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Seasons_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Seasons.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Seasons_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Seasons.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Seasons_Info(request):
    return JsonResponse(DSResponse(request=request, data=Seasons.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Seasons_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Seasons.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
