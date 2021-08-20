from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.votes.models.poll_votes import Poll_votes, Poll_votesManager


@JsonResponseWithException()
def Poll_votes_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Poll_votes.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Poll_votesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_votes_Add(request):
    return JsonResponse(DSResponseAdd(data=Poll_votes.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_votes_Update(request):
    return JsonResponse(DSResponseUpdate(data=Poll_votes.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_votes_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Poll_votes.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_votes_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Poll_votes.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_votes_Info(request):
    return JsonResponse(DSResponse(request=request, data=Poll_votes.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_votes_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Poll_votes.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
