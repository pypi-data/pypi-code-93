from galenSDK.exception.AuthenticationFailureException import AuthenticationFailureException
from galenSDK.exception.IllegalAuthorizationException import IlleglAuthorizationException
from galenSDK.exception.ItemNotFoundException import ItemNotFoundException


def check_http_status(response) -> bool:
    num = response.status_code
    if num == 200:
        return True
    if num == 201:
        return True
    if num == 207:
        raise IlleglAuthorizationException("207")
    if num == 401:
        raise AuthenticationFailureException(response.content)
    if num == 403:
        raise IlleglAuthorizationException(response.content)
    if num == 404:
        raise ItemNotFoundException(response.content)
    if num == 412:
        raise IlleglAuthorizationException(response.content)
    if num == 500:
        print(response.content)
        raise Exception("server-error")
    return False
