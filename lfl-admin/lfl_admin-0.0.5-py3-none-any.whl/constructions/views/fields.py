from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.constructions.models.fields import Fields, FieldsManager


@JsonResponseWithException()
def Fields_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Fields.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=FieldsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fields_Add(request):
    return JsonResponse(DSResponseAdd(data=Fields.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fields_Update(request):
    return JsonResponse(DSResponseUpdate(data=Fields.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fields_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Fields.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fields_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Fields.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fields_Info(request):
    return JsonResponse(DSResponse(request=request, data=Fields.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fields_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Fields.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
