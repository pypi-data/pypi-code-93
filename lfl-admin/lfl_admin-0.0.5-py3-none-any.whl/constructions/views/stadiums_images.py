from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.constructions.models.stadiums_images import Stadiums_images, Stadiums_imagesManager


@JsonResponseWithException()
def Stadiums_images_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Stadiums_images.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Stadiums_imagesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_images_Add(request):
    return JsonResponse(DSResponseAdd(data=Stadiums_images.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_images_Update(request):
    return JsonResponse(DSResponseUpdate(data=Stadiums_images.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_images_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Stadiums_images.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_images_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Stadiums_images.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_images_Info(request):
    return JsonResponse(DSResponse(request=request, data=Stadiums_images.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_images_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Stadiums_images.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
