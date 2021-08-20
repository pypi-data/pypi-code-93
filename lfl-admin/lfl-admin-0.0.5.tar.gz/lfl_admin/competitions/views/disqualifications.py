from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.disqualifications import Disqualifications, DisqualificationsManager


@JsonResponseWithException()
def Disqualifications_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Disqualifications.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=DisqualificationsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualifications_Add(request):
    return JsonResponse(DSResponseAdd(data=Disqualifications.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualifications_Update(request):
    return JsonResponse(DSResponseUpdate(data=Disqualifications.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualifications_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Disqualifications.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualifications_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Disqualifications.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualifications_Info(request):
    return JsonResponse(DSResponse(request=request, data=Disqualifications.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualifications_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Disqualifications.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
