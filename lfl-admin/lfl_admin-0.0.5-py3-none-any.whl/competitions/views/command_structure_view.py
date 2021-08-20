from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.command_structure_view import Command_structure_view, Command_structure_viewManager


@JsonResponseWithException(printing=True)
def Command_structure_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Command_structure_view.objects.
                filter().
                # select_related('amplua', 'club', 'formation', 'match', 'player', 'player_histories', 'region', 'user', 'tournament').
                get_range_rows1(
                request=request,
                function=Command_structure_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Command_structure_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Command_structure_view.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Command_structure_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Command_structure_view.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Command_structure_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Command_structure_view.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Command_structure_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Command_structure_view.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Command_structure_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Command_structure_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Command_structure_view_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Command_structure_view.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)

@JsonResponseWithException()
def Command_structure_view_Paste(request):
    return JsonResponse(DSResponse(request=request, data=Command_structure_view.objects.pasteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
