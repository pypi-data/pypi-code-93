from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.tournament_member_doubles import Tournament_member_doubles, Tournament_member_doublesManager


@JsonResponseWithException()
def Tournament_member_doubles_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Tournament_member_doubles.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Tournament_member_doublesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_member_doubles_Add(request):
    return JsonResponse(DSResponseAdd(data=Tournament_member_doubles.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_member_doubles_Update(request):
    return JsonResponse(DSResponseUpdate(data=Tournament_member_doubles.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_member_doubles_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_member_doubles.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_member_doubles_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_member_doubles.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_member_doubles_Info(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_member_doubles.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_member_doubles_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_member_doubles.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
