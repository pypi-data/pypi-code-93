from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.constructions.models.stadium_zones import Stadium_zones, Stadium_zonesManager


@JsonResponseWithException()
def Stadium_zones_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Stadium_zones.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Stadium_zonesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_zones_Add(request):
    return JsonResponse(DSResponseAdd(data=Stadium_zones.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_zones_Update(request):
    return JsonResponse(DSResponseUpdate(data=Stadium_zones.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_zones_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Stadium_zones.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_zones_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Stadium_zones.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_zones_Info(request):
    return JsonResponse(DSResponse(request=request, data=Stadium_zones.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_zones_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Stadium_zones.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
