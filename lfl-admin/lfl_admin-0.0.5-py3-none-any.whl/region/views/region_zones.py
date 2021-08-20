from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.region.models.region_zones import Region_zones, Region_zonesManager
from lfl_admin.region.models.region_zones_view import Region_zones_view, Region_zones_viewManager


@JsonResponseWithException()
def Region_zones_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Region_zones_view.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Region_zones_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zones_Add(request):
    return JsonResponse(DSResponseAdd(data=Region_zones.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zones_Update(request):
    return JsonResponse(DSResponseUpdate(data=Region_zones.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zones_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Region_zones.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zones_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Region_zones.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zones_Info(request):
    return JsonResponse(DSResponse(request=request, data=Region_zones.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zones_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Region_zones.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
