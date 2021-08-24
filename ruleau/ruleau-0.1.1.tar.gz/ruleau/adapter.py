import logging
from typing import TYPE_CHECKING, Any, AnyStr, Dict, List, Optional
from urllib.parse import urljoin

import requests

from ruleau.decorators import api_request
from ruleau.exceptions import APIException
from ruleau.process import Process
from ruleau.rule import Rule

if TYPE_CHECKING:
    from ruleau.structures import ExecutionResult

logger = logging.getLogger(__name__)


class ApiAdapter:
    base_url: AnyStr
    base_path: AnyStr
    api_key: Optional[AnyStr]

    def __init__(
        self,
        base_url: AnyStr,
        api_key: Optional[AnyStr] = None,
    ):
        """
        :param base_url: Base URL of the ruleau API
        :param api_key: (Optional) API key to authenticate with the API
        """
        self.base_url = base_url
        self.base_path = "/api/v1/"
        self.api_key = api_key

    @api_request
    def sync_case(self, case_id: AnyStr, process_id: AnyStr, payload: Dict) -> Dict:
        """
        Synchronise case with API
        :param case_id: The ID of the case being executed
        :param process_id: The ID of the process
        :param payload: Case payload to execute on
        :return:
        """
        response = requests.get(
            urljoin(
                self.base_url, f"{self.base_path}processes/{process_id}/cases/{case_id}"
            )
        )

        if response.status_code == 200:
            response = requests.patch(
                urljoin(
                    self.base_url,
                    f"{self.base_path}processes/{process_id}/cases/{case_id}",
                ),
                json={
                    "id": case_id,
                    "payload": payload,
                    "status": "OPEN",
                },
            )
            if response.status_code != 200:
                raise APIException(f"Failed to update case: {response.text}")

        elif response.status_code == 404:
            response = requests.post(
                urljoin(self.base_url, f"{self.base_path}processes/{process_id}/cases"),
                json={
                    "id": case_id,
                    "payload": payload,
                    "process": process_id,
                    "status": "OPEN",
                },
            )
            if response.status_code != 201:
                raise APIException(f"Failed to create case: {response.text}")

        else:
            raise APIException(f"Failed to check case: {response.text}")

        return response.json()

    @api_request
    def sync_process(self, process: Process):
        response = requests.post(
            urljoin(self.base_url, f"{self.base_path}processes"),
            json=process.parse(),
        )

        if response.status_code != 201:
            raise APIException(f"Unable to save rules: {response.text}")

        return response.json()

    @api_request
    def sync_results(
        self,
        process: "Process",
        case_id: AnyStr,
    ):
        payload = [
            {
                "rule": rule.id,
                "result": rule.execution_result.result,
                "payloads": rule.execution_result.payload.accessed
                if rule.execution_result.payload
                else None,
                "override": rule.execution_result.override,
                "original_result": rule.execution_result.original_result,
                "skipped": rule.execution_result.skipped,
            }
            for rule in process.rules
            if rule.execution_result
        ]
        response = requests.post(
            urljoin(
                self.base_url,
                f"{self.base_path}processes/{process.id}/cases/" f"{case_id}/results",
            ),
            json=payload,
        )
        if response.status_code > 299:
            raise APIException(
                f"Failed to store rule result for {case_id}: {response.text}"
            )
        return None

    @api_request
    def fetch_override(
        self, case_id: AnyStr, process_id: AnyStr, rule_id: AnyStr
    ) -> Optional[Dict[AnyStr, Any]]:
        """
        Fetch rule overrides
        :param case_id: client ID that identifies a previously established case
        :param process_id: The ID of the process that the case is being run against
        :param rule_id: The ID of the Rule to fetch overrides for
        :return: a ruleau overrides Optional[Dict[AnyStr, Any]]
        """
        response = requests.get(
            urljoin(
                self.base_url,
                f"{self.base_path}processes/{process_id}/"
                f"cases/{case_id}/overrides/search",
            ),
            params={"rule_id": rule_id},
        )
        if response.status_code != 200:
            return {}
        return response.json()
