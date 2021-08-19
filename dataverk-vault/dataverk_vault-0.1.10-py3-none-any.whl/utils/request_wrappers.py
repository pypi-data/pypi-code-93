import requests
import backoff


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=4)
def request_get_wrapper(url, **kwargs):
    return requests.get(url, **kwargs)


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=4)
def request_post_wrapper(url, **kwargs):
    return requests.post(url, **kwargs)
