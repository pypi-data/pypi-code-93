from minutes.models import NativeAd
from minutes.utils.api_auth import TokenAuthedViewSet
from ..common.serializers import NativeAdSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class NativeAdViewset(TokenAuthedViewSet):
    session_model = NativeAd
    queryset = NativeAd.objects.all()
    serializer_class = NativeAdSerializer
    pagination_class = None

    def update(self, request, pk=None):
        print(request.data)
        return super().update(request, pk)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        copy_from = self.queryset.get(id=pk)

        copied_data = {
            "handle": "Copy of {}".format(copy_from.handle),
            "sponsor": copy_from.sponsor,
            "lede": copy_from.lede,
            "body": copy_from.body,
            "campaign_title": copy_from.campaign_title,
            "campaign_link": copy_from.campaign_link,
            "pixels": copy_from.pixels,
        }

        new_ad = NativeAd(**copied_data)
        new_ad.save()

        return Response(self.serializer_class(new_ad).data)
