from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.user_ext.models.contacts_phones import Contacts_phones, Contacts_phonesManager


@JsonResponseWithException()
def Contacts_phones_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Contacts_phones.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Contacts_phonesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_phones_Add(request):
    return JsonResponse(DSResponseAdd(data=Contacts_phones.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_phones_Update(request):
    return JsonResponse(DSResponseUpdate(data=Contacts_phones.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_phones_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Contacts_phones.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_phones_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Contacts_phones.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_phones_Info(request):
    return JsonResponse(DSResponse(request=request, data=Contacts_phones.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Contacts_phones_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Contacts_phones.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
