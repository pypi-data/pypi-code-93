import math
from django.http import Http404
from minutes.models import Vertical
from rest_framework import serializers
from .edition import EditionSerializer


EDITIONS_PER_PAGE = 15


class VerticalSerializer(serializers.ModelSerializer):
    editions = serializers.SerializerMethodField()
    previous = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop("page", False)
        super().__init__(*args, **kwargs)

    def get_editions(self, obj):
        if self.page is None or self.page == "0":
            subset = obj.editions.all()
        else:
            page = int(self.page)
            offset = (page - 1) * EDITIONS_PER_PAGE
            limit = EDITIONS_PER_PAGE
            subset = obj.editions.all()[offset : offset + limit]

        return EditionSerializer(subset, many=True).data

    def get_next(self, obj):
        if self.page is None or self.page == "0":
            return None
        else:
            page = int(self.page)
            count = obj.editions.count()
            total_pages = self.get_count(obj)
            if count == 0 or page == total_pages:
                return None
            elif page > total_pages:
                raise Http404("Editions page does not exist.")
            else:
                return "?page={}".format(page + 1)

    def get_previous(self, obj):
        if self.page is None or self.page == "1" or self.page == "0":
            return None
        else:
            page = int(self.page)
            return "?page={}".format(page - 1)

    def get_count(self, obj):
        if self.page is None or self.page == "0":
            return None
        else:
            page = int(self.page)
            count = obj.editions.count()
            return math.ceil(count / EDITIONS_PER_PAGE)

    class Meta:
        model = Vertical
        fields = (
            "id",
            "name",
            "slug",
            "editions",
            "next",
            "previous",
            "count",
        )


class VerticalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vertical
        fields = ("id", "name", "slug")
