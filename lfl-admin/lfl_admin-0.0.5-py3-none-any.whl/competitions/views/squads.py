from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.squads import Squads, SquadsManager


@JsonResponseWithException()
def Squads_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Squads.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=SquadsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_Add(request):
    return JsonResponse(DSResponseAdd(data=Squads.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_Update(request):
    return JsonResponse(DSResponseUpdate(data=Squads.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Squads.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Squads.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_Info(request):
    return JsonResponse(DSResponse(request=request, data=Squads.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Squads.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
