def get_request_headers():
    from connexion import request
    try:
        headers = request.headers
    except RuntimeError:
        headers = None
    return headers


def get_request_context():
    try:
        from connexion import context
        assert context
    except (AssertionError, AttributeError):
        context = None
    return context


def get_request_access_token():
    headers = get_request_headers()
    token = None
    if headers is not None and headers.get('Authorization') is not None:
        token = headers['Authorization'].split(' ')[-1]
    return token


def safe_json_request(method, url, log_attributes=None, **kwargs):
    """Convenience function for calling external APIs to simplify error handling.

    :param method: HTTP methond (GET, POST, PUT, etc.)
    :param url: Request URL.
    :param kwargs: Additional parameters. See requests.request for details.
    :return: tuple of status_code and json body as a python dict
    """
    from tenacity import retry, stop_after_attempt, after_log, wait_random_exponential
    from requests import HTTPError, ConnectionError
    from stratus_api.core.logs import log_event
    import json
    status_code = None
    js = dict()
    if log_attributes is None:
        log_attributes = dict()

    @retry(stop=stop_after_attempt(3), reraise=True, wait=wait_random_exponential(multiplier=.5, max=3))
    def make_request():
        import requests
        from datetime import datetime
        start = datetime.utcnow()
        from requests.exceptions import HTTPError
        payload = dict(url=url, method=method)
        try:
            r = requests.request(method=method, url=url, **kwargs)
        except ConnectionError as e:
            log_event(level='info', start=start, end=datetime.utcnow(), status='failure', process_type='http_request',
                      payload=payload, attributes=log_attributes, failure_classification="Connection Error")
            raise e
        else:
            payload['status_code'] = r.status_code
            if r.status_code >= 400:
                results = json.dumps(
                    dict(
                        status_code=r.status_code,
                        response=format_response_body(response=r)
                    )
                )
                payload['response'] = format_response_body(response=r)
                failure_mapper = {400: 'Bad Request', 401: "Authentication Error", 403: "Authentication Error",
                                  404: "Not Found"}
                log_event(level='info', start=start, end=datetime.utcnow(), status='failure', process_type='request',
                          payload=payload, attributes=log_attributes, failure_classification=failure_mapper[
                        r.status_code] if r.status_code in failure_mapper.keys() else "Other Error")
                raise HTTPError(
                    results
                )
            else:
                log_event(level='info', start=start, end=datetime.utcnow(), status='success', process_type='request',
                          payload=payload, attributes=log_attributes)
            return r
    try:
        response = make_request()
    except ConnectionError:
        pass
    except HTTPError as exc:
        resp = json.loads(exc.args[0])
        status_code = resp['status_code']
        js = resp['response']
    else:
        status_code = response.status_code
        js = format_response_body(response=response)

    return status_code, js


def format_response_body(response):
    js = dict()
    try:
        js = response.json()
    except ValueError:
        js['content'] = response.text
    return js
