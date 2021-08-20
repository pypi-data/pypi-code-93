from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.region.models.region_zone_images import Region_zone_images, Region_zone_imagesManager


@JsonResponseWithException()
def Region_zone_images_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Region_zone_images.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Region_zone_imagesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zone_images_Add(request):
    return JsonResponse(DSResponseAdd(data=Region_zone_images.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zone_images_Update(request):
    return JsonResponse(DSResponseUpdate(data=Region_zone_images.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zone_images_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Region_zone_images.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zone_images_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Region_zone_images.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zone_images_Info(request):
    return JsonResponse(DSResponse(request=request, data=Region_zone_images.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Region_zone_images_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Region_zone_images.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
