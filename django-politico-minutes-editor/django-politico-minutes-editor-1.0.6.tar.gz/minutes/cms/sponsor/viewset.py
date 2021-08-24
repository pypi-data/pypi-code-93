from minutes.models import Sponsor
from minutes.utils.api_auth import TokenAuthedViewSet
from ..common.serializers import SponsorSerializer


class SponsorViewset(TokenAuthedViewSet):
    session_model = Sponsor
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer
    pagination_class = None
