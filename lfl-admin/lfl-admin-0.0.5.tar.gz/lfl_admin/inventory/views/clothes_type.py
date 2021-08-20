from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.inventory.models.clothes_type import Clothes_type, Clothes_typeManager


@JsonResponseWithException()
def Clothes_type_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Clothes_type.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Clothes_typeManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_type_Add(request):
    return JsonResponse(DSResponseAdd(data=Clothes_type.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_type_Update(request):
    return JsonResponse(DSResponseUpdate(data=Clothes_type.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_type_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Clothes_type.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_type_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Clothes_type.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_type_Info(request):
    return JsonResponse(DSResponse(request=request, data=Clothes_type.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Clothes_type_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Clothes_type.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
