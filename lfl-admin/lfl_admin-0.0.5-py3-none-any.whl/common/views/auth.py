from isc_common.http.DSResponse import JsonResponseWithException
from isc_common.http.response import JsonResponse
from lfl_admin.common.models.LoginRequets import LoginRequestEx


@JsonResponseWithException(printing=False)
def login(request):
    return JsonResponse(LoginRequestEx(request).response)
