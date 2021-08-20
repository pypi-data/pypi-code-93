from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.decor.models.banners_type import Banners_type, Banners_typeManager


@JsonResponseWithException()
def Banners_type_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Banners_type.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Banners_typeManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_type_Add(request):
    return JsonResponse(DSResponseAdd(data=Banners_type.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_type_Update(request):
    return JsonResponse(DSResponseUpdate(data=Banners_type.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_type_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Banners_type.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_type_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Banners_type.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_type_Info(request):
    return JsonResponse(DSResponse(request=request, data=Banners_type.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Banners_type_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Banners_type.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
