from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.disqualification_condition import Disqualification_condition, Disqualification_conditionManager


@JsonResponseWithException()
def Disqualification_condition_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Disqualification_condition.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Disqualification_conditionManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_condition_Add(request):
    return JsonResponse(DSResponseAdd(data=Disqualification_condition.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_condition_Update(request):
    return JsonResponse(DSResponseUpdate(data=Disqualification_condition.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_condition_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_condition.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_condition_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_condition.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_condition_Info(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_condition.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_condition_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_condition.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
