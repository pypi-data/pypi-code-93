from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.inventory.models.clothes_clubs import Clothes_clubs, Clothes_clubsManager


@JsonResponseWithException()
def Clothes_clubs_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Clothes_clubs.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Clothes_clubsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_clubs_Add(request):
    return JsonResponse(DSResponseAdd(data=Clothes_clubs.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_clubs_Update(request):
    return JsonResponse(DSResponseUpdate(data=Clothes_clubs.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_clubs_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Clothes_clubs.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_clubs_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Clothes_clubs.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_clubs_Info(request):
    return JsonResponse(DSResponse(request=request, data=Clothes_clubs.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_clubs_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Clothes_clubs.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
