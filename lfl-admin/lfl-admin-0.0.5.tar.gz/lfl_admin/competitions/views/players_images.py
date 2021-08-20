from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.players_images import Players_images, Players_imagesManager


@JsonResponseWithException()
def Players_images_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Players_images.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Players_imagesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_images_Add(request):
    return JsonResponse(DSResponseAdd(data=Players_images.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_images_Update(request):
    return JsonResponse(DSResponseUpdate(data=Players_images.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_images_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Players_images.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_images_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Players_images.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_images_Info(request):
    return JsonResponse(DSResponse(request=request, data=Players_images.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_images_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Players_images.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
