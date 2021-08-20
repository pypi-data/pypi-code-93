from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.user_ext.models.contacts import Contacts, ContactsManager


@JsonResponseWithException()
def Contacts_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Contacts.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=ContactsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_Add(request):
    return JsonResponse(DSResponseAdd(data=Contacts.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_Update(request):
    return JsonResponse(DSResponseUpdate(data=Contacts.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Contacts.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Contacts.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_Info(request):
    return JsonResponse(DSResponse(request=request, data=Contacts.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Contacts.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
