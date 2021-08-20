from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.common.models.site_lfl_images import Site_lfl_images, Site_lfl_imagesManager


@JsonResponseWithException()
def Site_lfl_images_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Site_lfl_images.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Site_lfl_imagesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Site_lfl_images_Add(request):
    return JsonResponse(DSResponseAdd(data=Site_lfl_images.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Site_lfl_images_Update(request):
    return JsonResponse(DSResponseUpdate(data=Site_lfl_images.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Site_lfl_images_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Site_lfl_images.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Site_lfl_images_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Site_lfl_images.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Site_lfl_images_Info(request):
    return JsonResponse(DSResponse(request=request, data=Site_lfl_images.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Site_lfl_images_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Site_lfl_images.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
