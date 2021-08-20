from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.formation import Formation, FormationManager


@JsonResponseWithException()
def Formation_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Formation.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=FormationManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Formation_Add(request):
    return JsonResponse(DSResponseAdd(data=Formation.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Formation_Update(request):
    return JsonResponse(DSResponseUpdate(data=Formation.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Formation_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Formation.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Formation_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Formation.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Formation_Info(request):
    return JsonResponse(DSResponse(request=request, data=Formation.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Formation_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Formation.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
