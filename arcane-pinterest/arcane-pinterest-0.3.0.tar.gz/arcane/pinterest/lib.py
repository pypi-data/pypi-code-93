import requests
import backoff
from typing import List
from datetime import datetime

from .exceptions import PinterestAsyncReportNotReadyException
from .pinterest import PinterestClient
from .types import PinterestReport


_PINTEREST_REPORT_READY_VALUE = 'FINISHED'

def get_pinterest_report(
    account_id: str,
    pinterest_client: PinterestClient,
    entity_fields: List[str],
    metrics: List[str],
    start_date: datetime,
    end_date: datetime
) -> PinterestReport:
    """ Does all the logic for getting an async Pinterest report (ie: Post Request > wait until the report is ready > get the url > retrieve data)

    Args:
        account_id (str): The account id
        pinterest_client (PinterestClient): The pinterest Client
        entity_fields (List[str]): Additional fields that you would like included for each entity in the Delivery Metrics Report. ⚠ Be careful when using this argument because asking a specific field can result in a failed request (ex: asking campaign_id when your level is CAMPAIGN is not supported as campaign_id is automatically included in CAMPAIGN level response)
        metrics (List[str]): Metrics that you want to have in the report
        start_date (datetime): Report start date. Start date and end date must be within 30 days of each other.
        end_date (datetime): Report end date.

    Raises:
        PinterestAsyncReportNotReadyException: Raised when the report is not yet ready after 10 backoff tentatives

    Returns:
        PinterestReport: Pinterest Report response as we get
    """

    @backoff.on_exception(backoff.expo, PinterestAsyncReportNotReadyException, max_tries=10)
    def _get_pinterest_report_url(account_id: str, token: str, pinterest_client: PinterestClient) -> str:
        reponse = pinterest_client.get_campaign_metrics(account_id, token).get('data', {})
        if reponse.get('report_status') != _PINTEREST_REPORT_READY_VALUE:
            pinterest_client.log(f"Pinterest report for account id {account_id} not ready yet")
            raise PinterestAsyncReportNotReadyException
        return reponse['url']


    pinterest_client.log(f"Getting Pinterest report token for account id {account_id}...")
    token = pinterest_client.post_advertiser_metrics_report(
        advertiser_id=account_id,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        entity_fields=entity_fields,
        metrics=metrics
    ).get('data', {}).get('token')

    pinterest_client.log(f"Retrieving report url for account id {account_id}")
    url = _get_pinterest_report_url(account_id, token, pinterest_client)

    reponse = requests.get(url)
    reponse.raise_for_status()

    return reponse.json()
