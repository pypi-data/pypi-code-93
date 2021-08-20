from django.contrib import admin
from minutes.models import (
    Edition,
    Minute,
    MinuteType,
    Interstitial,
    InterstitialType,
    Theme,
    Vertical,
    User,
    EditingSession,
    InterstitialInstance,
    Sponsor,
)

from minutes.tasks import publish, unpublish


class EditionAdmin(admin.ModelAdmin):
    actions = ["publish", "unpublish"]

    def publish(self, request, queryset):
        for e in queryset:
            publish.delay(e.id.hex)
        self.message_user(request, "Requested editions have been published.")

    def unpublish(self, request, queryset):
        for e in queryset:
            unpublish.delay(e.id.hex)
        self.message_user(request, "Requested editions have been unpublished.")


admin.site.register(Minute)
admin.site.register(Edition, EditionAdmin)
admin.site.register(MinuteType)
admin.site.register(Interstitial)
admin.site.register(InterstitialInstance)
admin.site.register(InterstitialType)
admin.site.register(Theme)
admin.site.register(Vertical)
admin.site.register(User)
admin.site.register(EditingSession)
admin.site.register(Sponsor)
