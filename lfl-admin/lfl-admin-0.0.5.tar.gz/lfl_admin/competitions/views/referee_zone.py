from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.referee_zone import Referee_zone, Referee_zoneManager


@JsonResponseWithException()
def Referee_zone_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Referee_zone.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Referee_zoneManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_zone_Add(request):
    return JsonResponse(DSResponseAdd(data=Referee_zone.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_zone_Update(request):
    return JsonResponse(DSResponseUpdate(data=Referee_zone.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_zone_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Referee_zone.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_zone_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Referee_zone.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_zone_Info(request):
    return JsonResponse(DSResponse(request=request, data=Referee_zone.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_zone_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Referee_zone.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
