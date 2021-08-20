from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.matches import Matches, MatchesManager


@JsonResponseWithException()
def Matches_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Matches.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=MatchesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matches_Add(request):
    return JsonResponse(DSResponseAdd(data=Matches.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matches_Update(request):
    return JsonResponse(DSResponseUpdate(data=Matches.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matches_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Matches.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matches_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Matches.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matches_Info(request):
    return JsonResponse(DSResponse(request=request, data=Matches.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Matches_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Matches.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
