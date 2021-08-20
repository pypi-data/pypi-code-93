from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.votes.models.polls import Polls, PollsManager


@JsonResponseWithException()
def Polls_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Polls.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=PollsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Polls_Add(request):
    return JsonResponse(DSResponseAdd(data=Polls.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Polls_Update(request):
    return JsonResponse(DSResponseUpdate(data=Polls.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Polls_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Polls.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Polls_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Polls.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Polls_Info(request):
    return JsonResponse(DSResponse(request=request, data=Polls.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Polls_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Polls.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
