from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.constructions.models.stadium_rating import Stadium_rating, Stadium_ratingManager


@JsonResponseWithException()
def Stadium_rating_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Stadium_rating.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Stadium_ratingManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_rating_Add(request):
    return JsonResponse(DSResponseAdd(data=Stadium_rating.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_rating_Update(request):
    return JsonResponse(DSResponseUpdate(data=Stadium_rating.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_rating_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Stadium_rating.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_rating_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Stadium_rating.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_rating_Info(request):
    return JsonResponse(DSResponse(request=request, data=Stadium_rating.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadium_rating_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Stadium_rating.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
