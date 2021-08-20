from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.decor.models.news_favorites import News_favorites, News_favoritesManager


@JsonResponseWithException()
def News_favorites_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=News_favorites.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=News_favoritesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_favorites_Add(request):
    return JsonResponse(DSResponseAdd(data=News_favorites.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_favorites_Update(request):
    return JsonResponse(DSResponseUpdate(data=News_favorites.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_favorites_Remove(request):
    return JsonResponse(DSResponse(request=request, data=News_favorites.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_favorites_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=News_favorites.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_favorites_Info(request):
    return JsonResponse(DSResponse(request=request, data=News_favorites.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def News_favorites_Copy(request):
    return JsonResponse(DSResponse(request=request, data=News_favorites.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
