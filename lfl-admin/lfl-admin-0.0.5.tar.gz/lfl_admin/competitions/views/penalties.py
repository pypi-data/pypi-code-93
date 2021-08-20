from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.penalties import Penalties, PenaltiesManager


@JsonResponseWithException()
def Penalties_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Penalties.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=PenaltiesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Penalties_Add(request):
    return JsonResponse(DSResponseAdd(data=Penalties.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Penalties_Update(request):
    return JsonResponse(DSResponseUpdate(data=Penalties.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Penalties_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Penalties.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Penalties_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Penalties.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Penalties_Info(request):
    return JsonResponse(DSResponse(request=request, data=Penalties.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Penalties_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Penalties.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
