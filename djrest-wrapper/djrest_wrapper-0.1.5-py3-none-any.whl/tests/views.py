from djrest_wrapper.interfaces import BaseViewSet
from .models import ExampleModel
from .service import ExampleService
from .serializers import ExampleResSerializer, ExmapleReqSerializer


class ExampleViewSet(BaseViewSet):
    queryset = ExampleModel.objects
    service = ExampleService(ExampleModel)
    serializer_action_classes = {
        'create': {
            'req': ExmapleReqSerializer,
            'res': ExampleResSerializer
        },
        'update': {
            'req': ExmapleReqSerializer,
            'res': ExampleResSerializer
        },
        'list': {
            'res': ExampleResSerializer
        },
        'retrieve': {
            'res': ExampleResSerializer
        },
    }
    page_result_key = 'examples'
