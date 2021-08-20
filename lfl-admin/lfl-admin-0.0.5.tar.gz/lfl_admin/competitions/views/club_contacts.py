from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.competitions.models.club_contacts import Club_contacts, Club_contactsManager


@JsonResponseWithException()
def Club_contacts_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Club_contacts.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Club_contactsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_contacts_Add(request):
    return JsonResponse(DSResponseAdd(data=Club_contacts.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_contacts_Update(request):
    return JsonResponse(DSResponseUpdate(data=Club_contacts.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_contacts_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Club_contacts.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_contacts_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Club_contacts.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_contacts_Info(request):
    return JsonResponse(DSResponse(request=request, data=Club_contacts.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Club_contacts_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Club_contacts.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
