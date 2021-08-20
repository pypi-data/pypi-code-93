from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.keepers import Keepers, KeepersManager


@JsonResponseWithException()
def Keepers_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Keepers.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=KeepersManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Keepers_Add(request):
    return JsonResponse(DSResponseAdd(data=Keepers.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Keepers_Update(request):
    return JsonResponse(DSResponseUpdate(data=Keepers.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Keepers_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Keepers.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Keepers_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Keepers.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Keepers_Info(request):
    return JsonResponse(DSResponse(request=request, data=Keepers.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Keepers_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Keepers.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
