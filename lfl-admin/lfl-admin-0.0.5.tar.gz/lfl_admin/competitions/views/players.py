from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.players_view import Players_viewManager, Players_view


@JsonResponseWithException()
def Players_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Players_view.objects.
                select_related('amplua', 'club').
                get_range_rows1(
                request=request,
                function=Players_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_Add(request):
    return JsonResponse(DSResponseAdd(data=Players.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_Update(request):
    return JsonResponse(DSResponseUpdate(data=Players.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Players.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Players.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_Info(request):
    return JsonResponse(DSResponse(request=request, data=Players_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Players_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Players.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
