import logging
import requests
from requests import RequestException

MAX_RESULTS_PER_PAGE = 200
MAX_RETRIES = 10


def fetch_paginated_response(
    url, user, api_key, json_array_key, extra_request_params=None
):
    """Fetches and returns an array of JSON responses from the given URL. Many of Last.fm's endpoints behave the same way by dividing
    results into "pages" of response objects. The only real difference between these endpoints is the type of response object returned,
    which can be specified here by the json_array_key parameter."""

    logging.debug("Fetching from " + url)
    paginated_json_responses = []
    page = 1
    total_pages = 1
    retries = 0
    while page <= total_pages:
        try:
            json_response = _send_request(
                url, _build_json_payload(user, api_key, page, extra_request_params)
            )
            logging.debug("Response: " + str(json_response))
            paginated_json_responses.append(json_response)
            total_pages = int(json_response[json_array_key]["@attr"]["totalPages"])
            page = page + 1
        except RequestException:
            if retries < MAX_RETRIES:
                logging.warning("Failed to fetch page " + str(page) + ". Retrying...")
                retries = retries + 1
            else:
                logging.warning(
                    "Failed to fetch page "
                    + str(page)
                    + " after "
                    + str(retries)
                    + " retries. Giving up and moving on..."
                )
                break

    return paginated_json_responses


def _send_request(url, json_payload):
    response = requests.get(url, params=json_payload)
    if response.ok:
        return response.json()
    else:
        response.raise_for_status()


def _build_json_payload(user, api_key, page, extra_request_params=None):
    payload = {
        "user": user,
        "format": "json",
        "api_key": api_key,
        "limit": MAX_RESULTS_PER_PAGE,
        "page": page,
    }

    if extra_request_params is not None:
        for param in extra_request_params:
            payload[param["key"]] = param["value"]

    return payload
