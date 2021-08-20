from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.region.models.cities import Cities, CitiesManager
from lfl_admin.region.models.cities_view import Cities_view, Cities_viewManager


@JsonResponseWithException()
def Cities_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Cities_view.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Cities_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cities_Add(request):
    return JsonResponse(DSResponseAdd(data=Cities.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cities_Update(request):
    return JsonResponse(DSResponseUpdate(data=Cities.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cities_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Cities.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cities_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Cities.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cities_Info(request):
    return JsonResponse(DSResponse(request=request, data=Cities.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cities_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Cities.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
