from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.leagues import Leagues
from lfl_admin.competitions.models.leagues_view import Leagues_view, Leagues_viewManager


@JsonResponseWithException()
def Leagues_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Leagues_view.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Leagues_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_Add(request):
    return JsonResponse(DSResponseAdd(data=Leagues.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_Update(request):
    return JsonResponse(DSResponseUpdate(data=Leagues.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Leagues.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Leagues.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_Info(request):
    return JsonResponse(DSResponse(request=request, data=Leagues.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Leagues_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Leagues.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
