from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.match_resaults import Match_resaults, Match_resaultsManager


@JsonResponseWithException()
def Match_resaults_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Match_resaults.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Match_resaultsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_resaults_Add(request):
    return JsonResponse(DSResponseAdd(data=Match_resaults.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_resaults_Update(request):
    return JsonResponse(DSResponseUpdate(data=Match_resaults.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_resaults_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Match_resaults.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_resaults_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Match_resaults.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_resaults_Info(request):
    return JsonResponse(DSResponse(request=request, data=Match_resaults.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Match_resaults_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Match_resaults.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
