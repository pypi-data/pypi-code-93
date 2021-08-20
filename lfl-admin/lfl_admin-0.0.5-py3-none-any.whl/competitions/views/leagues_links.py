from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.leagues_links import Leagues_links, Leagues_linksManager


@JsonResponseWithException()
def Leagues_links_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Leagues_links.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Leagues_linksManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_links_Add(request):
    return JsonResponse(DSResponseAdd(data=Leagues_links.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_links_Update(request):
    return JsonResponse(DSResponseUpdate(data=Leagues_links.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_links_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Leagues_links.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_links_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Leagues_links.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_links_Info(request):
    return JsonResponse(DSResponse(request=request, data=Leagues_links.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_links_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Leagues_links.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
