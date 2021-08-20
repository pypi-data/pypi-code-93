from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.squads_match import Squads_match, Squads_matchManager


@JsonResponseWithException()
def Squads_match_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Squads_match.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Squads_matchManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_match_Add(request):
    return JsonResponse(DSResponseAdd(data=Squads_match.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_match_Update(request):
    return JsonResponse(DSResponseUpdate(data=Squads_match.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_match_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Squads_match.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_match_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Squads_match.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_match_Info(request):
    return JsonResponse(DSResponse(request=request, data=Squads_match.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Squads_match_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Squads_match.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
