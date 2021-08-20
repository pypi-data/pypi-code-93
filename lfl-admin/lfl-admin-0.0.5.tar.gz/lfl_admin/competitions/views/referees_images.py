from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.referees_images import Referees_images, Referees_imagesManager


@JsonResponseWithException()
def Referees_images_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Referees_images.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Referees_imagesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_images_Add(request):
    return JsonResponse(DSResponseAdd(data=Referees_images.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_images_Update(request):
    return JsonResponse(DSResponseUpdate(data=Referees_images.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_images_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Referees_images.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_images_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Referees_images.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_images_Info(request):
    return JsonResponse(DSResponse(request=request, data=Referees_images.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_images_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Referees_images.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
