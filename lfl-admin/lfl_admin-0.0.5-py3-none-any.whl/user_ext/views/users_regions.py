from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.user_ext.models.users_regions import Users_regions, Users_regionsManager


@JsonResponseWithException()
def Users_regions_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Users_regions.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Users_regionsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_regions_Add(request):
    return JsonResponse(DSResponseAdd(data=Users_regions.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_regions_Update(request):
    return JsonResponse(DSResponseUpdate(data=Users_regions.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_regions_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Users_regions.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_regions_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Users_regions.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_regions_Info(request):
    return JsonResponse(DSResponse(request=request, data=Users_regions.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_regions_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Users_regions.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
