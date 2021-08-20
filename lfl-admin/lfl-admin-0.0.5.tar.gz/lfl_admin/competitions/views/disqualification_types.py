from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.disqualification_types import Disqualification_types, Disqualification_typeManager


@JsonResponseWithException()
def Disqualification_types_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Disqualification_types.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Disqualification_typeManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_types_Add(request):
    return JsonResponse(DSResponseAdd(data=Disqualification_types.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_types_Update(request):
    return JsonResponse(DSResponseUpdate(data=Disqualification_types.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_types_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_types.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_types_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_types.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_types_Info(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_types.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Disqualification_types_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Disqualification_types.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
