from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.decor.models.news import News, NewsManager


@JsonResponseWithException()
def News_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=News.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=NewsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_Add(request):
    return JsonResponse(DSResponseAdd(data=News.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_Update(request):
    return JsonResponse(DSResponseUpdate(data=News.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_Remove(request):
    return JsonResponse(DSResponse(request=request, data=News.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=News.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_Info(request):
    return JsonResponse(DSResponse(request=request, data=News.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_Copy(request):
    return JsonResponse(DSResponse(request=request, data=News.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
