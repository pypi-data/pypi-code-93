from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.tournaments_images import Tournaments_images, Tournaments_imagesManager


@JsonResponseWithException()
def Tournaments_images_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Tournaments_images.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Tournaments_imagesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournaments_images_Add(request):
    return JsonResponse(DSResponseAdd(data=Tournaments_images.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournaments_images_Update(request):
    return JsonResponse(DSResponseUpdate(data=Tournaments_images.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournaments_images_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Tournaments_images.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournaments_images_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Tournaments_images.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournaments_images_Info(request):
    return JsonResponse(DSResponse(request=request, data=Tournaments_images.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournaments_images_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Tournaments_images.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
