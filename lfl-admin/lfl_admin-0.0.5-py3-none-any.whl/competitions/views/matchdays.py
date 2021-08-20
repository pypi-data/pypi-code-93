from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.matchdays import Matchdays, MatchdaysManager


@JsonResponseWithException()
def Matchdays_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Matchdays.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=MatchdaysManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matchdays_Add(request):
    return JsonResponse(DSResponseAdd(data=Matchdays.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matchdays_Update(request):
    return JsonResponse(DSResponseUpdate(data=Matchdays.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matchdays_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Matchdays.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matchdays_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Matchdays.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matchdays_Info(request):
    return JsonResponse(DSResponse(request=request, data=Matchdays.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matchdays_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Matchdays.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
