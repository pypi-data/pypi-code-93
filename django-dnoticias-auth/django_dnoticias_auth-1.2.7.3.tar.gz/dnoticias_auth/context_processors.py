from django.conf import settings

def keycloak(request):
    return {
        "OIDC_OP_AUTHENTICATION_ENDPOINT" : settings.OIDC_OP_AUTHENTICATION_ENDPOINT
    }