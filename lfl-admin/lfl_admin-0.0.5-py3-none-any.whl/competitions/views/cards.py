from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.cards import Cards, CardsManager


@JsonResponseWithException()
def Cards_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Cards.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=CardsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cards_Add(request):
    return JsonResponse(DSResponseAdd(data=Cards.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cards_Update(request):
    return JsonResponse(DSResponseUpdate(data=Cards.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cards_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Cards.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cards_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Cards.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cards_Info(request):
    return JsonResponse(DSResponse(request=request, data=Cards.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Cards_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Cards.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
