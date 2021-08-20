from django.db import models

from cms.models import CMSPlugin
from filer.fields.image import FilerImageField
from mixins.models import VideoURLMixin


class ContentWidthVideo(CMSPlugin, VideoURLMixin):
    """
    Represents a content width video object
    """

    image = FilerImageField(related_name="+", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=128, blank=True)
    alt_title = models.CharField(max_length=128, blank=True, default="")
    alt_text = models.CharField(max_length=128, blank=True, default="")
    display_image = models.BooleanField(default=True)

    def __str__(self):
        """
        String representation of the object
        """
        return f"Content Width Video {self.pk}"
