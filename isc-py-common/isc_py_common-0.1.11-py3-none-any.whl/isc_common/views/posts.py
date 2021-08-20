from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.common.models.posts import Posts, PostsManager


@JsonResponseWithException()
def Posts_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Posts.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=PostsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posts_Add(request):
    return JsonResponse(DSResponseAdd(data=Posts.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posts_Update(request):
    return JsonResponse(DSResponseUpdate(data=Posts.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posts_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Posts.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posts_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Posts.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posts_Info(request):
    return JsonResponse(DSResponse(request=request, data=Posts.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Posts_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Posts.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
