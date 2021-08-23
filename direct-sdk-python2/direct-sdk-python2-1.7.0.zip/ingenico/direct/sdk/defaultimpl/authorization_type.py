class AuthorizationType:

    V1HMAC = "v1HMAC"
    AUTHORIZATION_TYPES = [V1HMAC]

    @staticmethod
    def get_authorization(name):
        for authType in AuthorizationType.AUTHORIZATION_TYPES:
            if name.lower() == authType.lower():
                return authType
        raise RuntimeError("Authorization '{}' not found".format(name))
