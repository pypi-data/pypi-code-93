from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.tournament_members import Tournament_members, Tournament_membersManager


@JsonResponseWithException()
def Tournament_members_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Tournament_members.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Tournament_membersManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_members_Add(request):
    return JsonResponse(DSResponseAdd(data=Tournament_members.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_members_Update(request):
    return JsonResponse(DSResponseUpdate(data=Tournament_members.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_members_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_members.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_members_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_members.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_members_Info(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_members.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Tournament_members_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Tournament_members.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
