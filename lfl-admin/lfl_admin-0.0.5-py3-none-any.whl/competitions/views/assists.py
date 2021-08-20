from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.assists import Assists, AssistsManager


@JsonResponseWithException()
def Assists_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Assists.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=AssistsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Assists_Add(request):
    return JsonResponse(DSResponseAdd(data=Assists.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Assists_Update(request):
    return JsonResponse(DSResponseUpdate(data=Assists.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Assists_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Assists.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Assists_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Assists.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Assists_Info(request):
    return JsonResponse(DSResponse(request=request, data=Assists.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Assists_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Assists.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
