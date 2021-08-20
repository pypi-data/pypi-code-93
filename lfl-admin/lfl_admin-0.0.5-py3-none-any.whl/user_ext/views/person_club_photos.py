from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.user_ext.models.person_club_photos import Person_club_photos, Person_club_photosManager


@JsonResponseWithException()
def Person_club_photos_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Person_club_photos.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Person_club_photosManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Person_club_photos_Add(request):
    return JsonResponse(DSResponseAdd(data=Person_club_photos.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Person_club_photos_Update(request):
    return JsonResponse(DSResponseUpdate(data=Person_club_photos.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Person_club_photos_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Person_club_photos.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Person_club_photos_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Person_club_photos.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Person_club_photos_Info(request):
    return JsonResponse(DSResponse(request=request, data=Person_club_photos.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Person_club_photos_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Person_club_photos.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
