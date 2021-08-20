from isc_common.http.DSResponse import DSResponse, JsonWSPostResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from reports.models.jasper_reports import get_reports


@JsonWSPostResponseWithException()
def JasperReports_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=get_reports(request=request),
            status=RPCResponseConstant.statusSuccess).response)
