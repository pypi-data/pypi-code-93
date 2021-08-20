from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.region.models.city_images import City_images, City_imagesManager


@JsonResponseWithException()
def City_images_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=City_images.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=City_imagesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def City_images_Add(request):
    return JsonResponse(DSResponseAdd(data=City_images.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def City_images_Update(request):
    return JsonResponse(DSResponseUpdate(data=City_images.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def City_images_Remove(request):
    return JsonResponse(DSResponse(request=request, data=City_images.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def City_images_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=City_images.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def City_images_Info(request):
    return JsonResponse(DSResponse(request=request, data=City_images.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def City_images_Copy(request):
    return JsonResponse(DSResponse(request=request, data=City_images.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
