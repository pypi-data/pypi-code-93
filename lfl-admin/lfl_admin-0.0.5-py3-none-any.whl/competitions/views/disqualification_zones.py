from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.disqualification_zones import Disqualification_zones
from lfl_admin.competitions.models.disqualification_zones_view import Disqualification_zones_view, Disqualification_zones_viewManager


@JsonResponseWithException()
def Disqualification_zones_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Disqualification_zones_view.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Disqualification_zones_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_zones_Add(request):
    return JsonResponse(DSResponseAdd(data=Disqualification_zones.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_zones_Update(request):
    return JsonResponse(DSResponseUpdate(data=Disqualification_zones.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_zones_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_zones.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_zones_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_zones.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_zones_Info(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_zones_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_zones_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_zones.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
