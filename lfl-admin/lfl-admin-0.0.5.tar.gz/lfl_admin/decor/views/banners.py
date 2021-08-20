from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.decor.models.banners import Banners, BannersManager


@JsonResponseWithException()
def Banners_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Banners.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=BannersManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_Add(request):
    return JsonResponse(DSResponseAdd(data=Banners.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_Update(request):
    return JsonResponse(DSResponseUpdate(data=Banners.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Banners.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Banners.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_Info(request):
    return JsonResponse(DSResponse(request=request, data=Banners.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Banners.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
