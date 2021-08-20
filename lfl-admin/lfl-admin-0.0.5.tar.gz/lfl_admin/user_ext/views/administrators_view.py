from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.user_ext.models.administrators import Administrators

from lfl_admin.user_ext.models.administrators_view import Administrators_view, Administrators_viewManager


@JsonResponseWithException()
def Administrators_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Administrators_view.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Administrators_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Administrators.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Administrators.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Administrators.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Administrators_view.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Administrators_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_view_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Administrators_view.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
