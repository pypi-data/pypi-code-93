from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.statistic.models.import_command_stuctures import Import_command_stuctures, Import_command_stucturesManager


@JsonResponseWithException()
def Import_command_stuctures_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Import_command_stuctures.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Import_command_stucturesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_Add(request):
    return JsonResponse(DSResponseAdd(data=Import_command_stuctures.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_Update(request):
    return JsonResponse(DSResponseUpdate(data=Import_command_stuctures.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Import_command_stuctures.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Import_command_stuctures.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_Info(request):
    return JsonResponse(DSResponse(request=request, data=Import_command_stuctures.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Import_command_stuctures.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
