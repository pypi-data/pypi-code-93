from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.statistic.models.import_command_stuctures_log import Import_command_stuctures_log, Import_command_stuctures_logManager


@JsonResponseWithException()
def Import_command_stuctures_log_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Import_command_stuctures_log.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Import_command_stuctures_logManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_log_Add(request):
    return JsonResponse(DSResponseAdd(data=Import_command_stuctures_log.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_log_Update(request):
    return JsonResponse(DSResponseUpdate(data=Import_command_stuctures_log.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_log_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Import_command_stuctures_log.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_log_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Import_command_stuctures_log.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_log_Info(request):
    return JsonResponse(DSResponse(request=request, data=Import_command_stuctures_log.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Import_command_stuctures_log_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Import_command_stuctures_log.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
