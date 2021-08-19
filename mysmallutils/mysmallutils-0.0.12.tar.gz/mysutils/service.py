def endpoint(service: str = '') -> str:
    """ Obtain the final URL to the service dynamically from a request.

    :param request: The request to obtain the URL.
    :param service: The path to the services to join with the request base.
    :return: A string with the URL.
    """
    base_url = '<script>document.write(window.location.href);</script>'
    if base_url.endswith('/') and service.startswith('/'):
        return base_url[:-1] + service
    if not base_url.endswith('/') and not service.startswith('/'):
        return base_url + '/' + service
    return base_url + service
