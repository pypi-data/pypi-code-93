from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.divisions_images import Divisions_images, Divisions_imagesManager


@JsonResponseWithException()
def Divisions_images_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Divisions_images.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Divisions_imagesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_images_Add(request):
    return JsonResponse(DSResponseAdd(data=Divisions_images.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_images_Update(request):
    return JsonResponse(DSResponseUpdate(data=Divisions_images.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_images_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Divisions_images.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_images_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Divisions_images.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_images_Info(request):
    return JsonResponse(DSResponse(request=request, data=Divisions_images.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_images_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Divisions_images.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
