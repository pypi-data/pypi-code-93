from minutes.models import Vertical

from minutes.api.common.serializers import VerticalEditionsSerializer
from minutes.api.common.viewsets import BaseApiReadOnlyViewset


class VerticalViewset(BaseApiReadOnlyViewset):
    queryset = Vertical.objects.all()
    serializer_class = VerticalEditionsSerializer
    lookup_field = "slug"
