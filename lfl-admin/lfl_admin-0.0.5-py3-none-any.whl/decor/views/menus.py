from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.decor.models.menus import Menus, MenusManager


@JsonResponseWithException()
def Menus_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Menus.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=MenusManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Menus_Add(request):
    return JsonResponse(DSResponseAdd(data=Menus.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Menus_Update(request):
    return JsonResponse(DSResponseUpdate(data=Menus.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Menus_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Menus.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Menus_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Menus.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Menus_Info(request):
    return JsonResponse(DSResponse(request=request, data=Menus.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Menus_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Menus.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
