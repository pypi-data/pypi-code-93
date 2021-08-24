from django.contrib import admin

from ob_dj_otp.core.otp.models import OneTruePairing


class OneTruePairingAdmin(admin.ModelAdmin):
    """ OneTruePairingAdmin
    """

    list_display = (
        "phone_number",
        "usage",
        "status",
        "created_at",
        "verification_code",
    )
    model = OneTruePairing


admin.site.register(OneTruePairing, OneTruePairingAdmin)
