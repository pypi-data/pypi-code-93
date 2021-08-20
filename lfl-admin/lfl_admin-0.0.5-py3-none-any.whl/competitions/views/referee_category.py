from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.referee_category import Referee_category, Referee_categoryManager


@JsonResponseWithException()
def Referee_category_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Referee_category.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Referee_categoryManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_category_Add(request):
    return JsonResponse(DSResponseAdd(data=Referee_category.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_category_Update(request):
    return JsonResponse(DSResponseUpdate(data=Referee_category.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_category_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Referee_category.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_category_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Referee_category.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_category_Info(request):
    return JsonResponse(DSResponse(request=request, data=Referee_category.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_category_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Referee_category.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
