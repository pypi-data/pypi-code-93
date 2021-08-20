from isc_common.common import shirts
from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.inventory.models.clothes import Clothes, ClothesManager
from lfl_admin.inventory.models.clothes_view import Clothes_view, Clothes_viewManager


@JsonResponseWithException()
def Clothes_Fetch(request):
    _request = DSRequest(request)
    query = Clothes_view.objects.filter()

    clothes_type_code = _request.get_data().get('clothes_type_code')
    if clothes_type_code is not None:
        query = Clothes_view.objects.filter(clothes_type_code=clothes_type_code)

    return JsonResponse(
        DSResponse(
            request=request,
            data=query.
                get_range_rows1(
                request=request,
                function=Clothes_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_Add(request):
    return JsonResponse(DSResponseAdd(data=Clothes.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_Update(request):
    return JsonResponse(DSResponseUpdate(data=Clothes.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Clothes.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Clothes.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_Info(request):
    return JsonResponse(DSResponse(request=request, data=Clothes_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Clothes.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
