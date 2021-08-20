from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.club_admins import Club_admins, Club_adminsManager


@JsonResponseWithException()
def Club_admins_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Club_admins.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Club_adminsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_admins_Add(request):
    return JsonResponse(DSResponseAdd(data=Club_admins.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_admins_Update(request):
    return JsonResponse(DSResponseUpdate(data=Club_admins.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_admins_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Club_admins.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_admins_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Club_admins.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_admins_Info(request):
    return JsonResponse(DSResponse(request=request, data=Club_admins.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_admins_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Club_admins.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
