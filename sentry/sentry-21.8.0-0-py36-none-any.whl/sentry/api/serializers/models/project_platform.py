from sentry.api.serializers import Serializer, register
from sentry.models import ProjectPlatform


@register(ProjectPlatform)
class ProjectPlatformSerializer(Serializer):
    """
    Tracks usage of a platform for a given project.

    Note: This model is used solely for analytics.
    """

    def serialize(self, obj, attrs, user):
        return {"platform": obj.platform, "dateCreated": obj.date_added}
