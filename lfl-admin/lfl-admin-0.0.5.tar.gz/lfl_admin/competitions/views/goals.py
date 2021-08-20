from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.goals import Goals, GoalsManager


@JsonResponseWithException()
def Goals_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Goals.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=GoalsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Goals_Add(request):
    return JsonResponse(DSResponseAdd(data=Goals.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Goals_Update(request):
    return JsonResponse(DSResponseUpdate(data=Goals.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Goals_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Goals.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Goals_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Goals.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Goals_Info(request):
    return JsonResponse(DSResponse(request=request, data=Goals.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Goals_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Goals.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
