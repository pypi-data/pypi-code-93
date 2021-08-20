from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.user_ext.models.Administrators_upload_image import DSResponse_Administrators_UploadImage
from lfl_admin.user_ext.models.administrators import Administrators, AdministratorsManager


@JsonResponseWithException()
def Administrators_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Administrators.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=AdministratorsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_Add(request):
    return JsonResponse(DSResponseAdd(data=Administrators.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_Update(request):
    return JsonResponse(DSResponseUpdate(data=Administrators.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Administrators.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Administrators.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_Info(request):
    return JsonResponse(DSResponse(request=request, data=Administrators.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Administrators.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Administrators_ImagesUpload(request):
    DSResponse_Administrators_UploadImage(request)
    return JsonResponse(dict(status=RPCResponseConstant.statusSuccess))
