from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.referees import Referees
from lfl_admin.competitions.models.referees_view import Referees_viewManager, Referees_view


@JsonResponseWithException()
def Referees_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Referees_view.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Referees_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_Add(request):
    return JsonResponse(DSResponseAdd(data=Referees.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_Update(request):
    return JsonResponse(DSResponseUpdate(data=Referees.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Referees.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Referees.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_Info(request):
    return JsonResponse(DSResponse(request=request, data=Referees_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Referees_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Referees.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
