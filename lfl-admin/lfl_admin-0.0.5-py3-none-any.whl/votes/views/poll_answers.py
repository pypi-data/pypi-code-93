from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.votes.models.poll_answers import Poll_answers, Poll_answersManager


@JsonResponseWithException()
def Poll_answers_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Poll_answers.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Poll_answersManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_answers_Add(request):
    return JsonResponse(DSResponseAdd(data=Poll_answers.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_answers_Update(request):
    return JsonResponse(DSResponseUpdate(data=Poll_answers.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_answers_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Poll_answers.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_answers_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Poll_answers.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_answers_Info(request):
    return JsonResponse(DSResponse(request=request, data=Poll_answers.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Poll_answers_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Poll_answers.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
