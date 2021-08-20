from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.fouls import Fouls, FoulsManager


@JsonResponseWithException()
def Fouls_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Fouls.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=FoulsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fouls_Add(request):
    return JsonResponse(DSResponseAdd(data=Fouls.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fouls_Update(request):
    return JsonResponse(DSResponseUpdate(data=Fouls.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fouls_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Fouls.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fouls_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Fouls.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fouls_Info(request):
    return JsonResponse(DSResponse(request=request, data=Fouls.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fouls_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Fouls.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
