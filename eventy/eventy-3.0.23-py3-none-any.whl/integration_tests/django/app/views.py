from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from eventy.trace_id import correlation_id_var


@require_GET
def health(request):
    return HttpResponse('OK')


def hello(request):
    return JsonResponse({'hello': correlation_id_var.get()})
