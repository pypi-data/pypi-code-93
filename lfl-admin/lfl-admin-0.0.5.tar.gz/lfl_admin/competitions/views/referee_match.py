from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.referee_match import Referee_match, Referee_matchManager


@JsonResponseWithException()
def Referee_match_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Referee_match.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Referee_matchManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_match_Add(request):
    return JsonResponse(DSResponseAdd(data=Referee_match.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_match_Update(request):
    return JsonResponse(DSResponseUpdate(data=Referee_match.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_match_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Referee_match.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_match_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Referee_match.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_match_Info(request):
    return JsonResponse(DSResponse(request=request, data=Referee_match.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referee_match_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Referee_match.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
