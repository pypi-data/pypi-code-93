from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.fines import Fines, FinesManager


@JsonResponseWithException()
def Fines_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Fines.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=FinesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fines_Add(request):
    return JsonResponse(DSResponseAdd(data=Fines.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fines_Update(request):
    return JsonResponse(DSResponseUpdate(data=Fines.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fines_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Fines.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fines_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Fines.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fines_Info(request):
    return JsonResponse(DSResponse(request=request, data=Fines.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fines_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Fines.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
