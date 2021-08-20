from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException, JsonWSResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.divisions import Divisions
from lfl_admin.competitions.models.divisions_view import Divisions_view, Divisions_viewManager


@JsonWSResponseWithException()
def Divisions_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Divisions_view.objects.
                exclude().
                get_range_rows1(
                request=request,
                function=Divisions_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_Add(request):
    return JsonResponse(DSResponseAdd(data=Divisions.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_Update(request):
    return JsonResponse(DSResponseUpdate(data=Divisions.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Divisions.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Divisions.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_Info(request):
    return JsonResponse(DSResponse(request=request, data=Divisions_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Divisions_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Divisions.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
