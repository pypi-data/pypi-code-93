import os
import json
import random
import requests
import math
from typing import List, Dict, Optional

from tqdm import tqdm
from loguru import logger


class Connection:
    def __init__(self, org_id: int):
        self._initialize(org_id)

    def _initialize(self, org_id: int):

        email = os.getenv("USER_MAIL")
        password = os.getenv("USER_PASS")

        if not password:
            raise ValueError("Credentials for API access is not set, please check")

        auth_payload = {"email": email, "password": password}

        auth_headers = {"Content-Type": "application/json"}

        auth_token = self._post_request(
            level="authorisation", payload=auth_payload, header=auth_headers
        ).get("access_token")

        change_org_payload = {"organisation_id": int(org_id)}

        change_org_header = {"Authorization": "Bearer %s" % auth_token}

        self.access_token = self._post_request(
            level="change_org", payload=change_org_payload, header=change_org_header
        ).get("access_token")

    def _post_request(self, level: str, payload: dict, header: dict) -> Dict:

        if level == "authorisation":
            url = os.getenv("AUTH_URL")
        elif level == "change_org":
            url = os.getenv("ORG_URL")
        else:
            raise NotImplementedError(
                "Currently only authorisation and change org post requests are supported"
            )

        if not url:
            raise ValueError("Credentials for API access is not set, please check")

        response = requests.post(url, headers=header, json=payload)

        if response.status_code != 200:
            raise ConnectionError(
                f"Status code {response.status_code} returned. text: {response.text}"
            )

        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            raise ValueError(
                f"Status code {response.status_code} returned. text: {response.text}"
            )

    def _get_request(
        self, level: str, params: dict, call_uuid: Optional[str] = ""
    ) -> Dict:
        headers = {"Authorization": "Bearer %s" % self.access_token}
        if level == "call":
            url = os.getenv("CALL_URL")
        elif level == "turn":
            if not call_uuid:
                raise AttributeError(
                    "Call UUID needs to be assigned for turn level requests"
                )
            url = os.getenv("TURN_URL")
        else:
            raise NotImplementedError(
                "Currently only call and turn level get requests are supported"
            )

        if url:
            url = url.format(call_uuid)
            try:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code != 200:
                    print(
                        f"Status code {response.status_code} returned. text: {response.text}"
                    )

                return response.json()
            except json.decoder.JSONDecodeError:
                raise RuntimeError(
                    f"Status code {response.status_code} returned. text: {response.text}"
                )
        raise ValueError("Environment variable $TURN_URL was not set.")

    def fetch_calls(
        self,
        lang_code: str,
        start: str,
        end: str,
        call_quantity: int,
        flow_uuid: Optional[str] = None,
        page_size: int = 20,
        custom_search_key: Optional[str] = None,
        custom_search_value: Optional[str] = None,
        subtesting: bool = False,
    ) -> List:
        params = {
            "start": start,
            "end": end,
            "lang_code": lang_code,
            "page_size": page_size,
            "call_type": "subtesting" if subtesting else "live",
            "ignored_caller_numbers": ["0000000000", "ev-connect"],
        }

        PAGE_SCAN_LIMIT = math.ceil(call_quantity / page_size)

        if flow_uuid:
            params["flow_uuid"] = flow_uuid

        if custom_search_key:
            params["custom_search_key"] = custom_search_key
            params["custom_search_value"] = custom_search_value

        # Call Report API is Paginated so data is saved in pages, each page will be a get request
        logger.info(params)

        first_page = self._get_request("call", params)
        current_page = first_page.get("page", 1)
        total_pages = first_page.get("total_pages", 2)
        call_summary = first_page.get("items", [])
        if PAGE_SCAN_LIMIT < total_pages:
            pages_to_read = random.sample(
                range(current_page, total_pages), PAGE_SCAN_LIMIT
            )
        else:
            pages_to_read = list(range(current_page, total_pages))
        logger.info(f"Reading random {len(pages_to_read)} pages.")

        for page in tqdm(pages_to_read):
            params["page"] = page
            logger.info(params)
            items = self._get_request("call", params).get("items", [])
            call_summary.extend(items)

        if call_summary:
            if call_quantity and call_quantity < len(call_summary):
                return random.sample(call_summary, call_quantity)
            return call_summary
        else:
            raise EOFError("No calls found, please check your parameters")

    def fetch_turns(self, call_uuid: str) -> Dict:
        params = {"page_size": 100}

        return self._get_request("turn", params=params, call_uuid=call_uuid)
