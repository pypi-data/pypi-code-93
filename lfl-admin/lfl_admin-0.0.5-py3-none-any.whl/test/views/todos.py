from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from lfl_admin.test.models.todos import Todos, TodosManager


@JsonResponseWithException()
def Todos_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Todos.objects.
                filter().
                get_range_rows1(
                request=request,
                function=TodosManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Todos_Add(request):
    return JsonResponse(DSResponseAdd(data=Todos.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Todos_Update(request):
    return JsonResponse(DSResponseUpdate(data=Todos.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Todos_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Todos.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Todos_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Todos.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Todos_Info(request):
    return JsonResponse(DSResponse(request=request, data=Todos.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Todos_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Todos.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
