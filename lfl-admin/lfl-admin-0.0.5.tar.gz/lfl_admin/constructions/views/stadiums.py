from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.constructions.models.stadiums import Stadiums, StadiumsManager


@JsonResponseWithException()
def Stadiums_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Stadiums.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=StadiumsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_Add(request):
    return JsonResponse(DSResponseAdd(data=Stadiums.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_Update(request):
    return JsonResponse(DSResponseUpdate(data=Stadiums.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Stadiums.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Stadiums.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_Info(request):
    return JsonResponse(DSResponse(request=request, data=Stadiums.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Stadiums_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Stadiums.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
