from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.clubs_clothes import Clubs_clothes, Clubs_clothesManager


@JsonResponseWithException()
def Clubs_clothes_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Clubs_clothes.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Clubs_clothesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clubs_clothes_Add(request):
    return JsonResponse(DSResponseAdd(data=Clubs_clothes.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clubs_clothes_Update(request):
    return JsonResponse(DSResponseUpdate(data=Clubs_clothes.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clubs_clothes_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Clubs_clothes.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clubs_clothes_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Clubs_clothes.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clubs_clothes_Info(request):
    return JsonResponse(DSResponse(request=request, data=Clubs_clothes.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clubs_clothes_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Clubs_clothes.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
