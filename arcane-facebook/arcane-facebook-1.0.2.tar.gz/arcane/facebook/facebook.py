import json
import logging
import time
import warnings
from typing import List, Dict, Optional
from typing_extensions import TypedDict
import backoff

from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError

from .exceptions import FacebookAccountLostAccessException

AVAILAIBLE_BREAKDOWNS = ['age', 'country', 'dma', 'gender', 'frequency_value',
                         'hourly_stats_aggregated_by_advertiser_time_zone',
                         'hourly_stats_aggregated_by_audience_time_zone', 'impression_device', 'place_page_id',
                         'publisher_platform', 'platform_position', 'device_platform', 'product_id', 'region',
                         'ad_format_asset', 'body_asset', 'call_to_action_asset', 'description_asset', 'image_asset',
                         'link_url_asset', 'title_asset', 'video_asset']

AVAILABLE_FIELDS = ['account_id', 'account_currency',  'account_name', 'actions', 'action_values', 'adset_id', 'adset_name', 'ad_id', 'ad_name', 'campaign_id', 'campaign_name',
                    'clicks', 'date_start', 'date_stop', 'impressions', 'objective', 'reach', 'spend', 'unique_actions']

AVAILABLE_DATE_PRESET = ['last_3d','last_30d','this_month','this_year','maximum', 'last_year']

AVAILABLE_TIME_INCREMENTS = ['monthly', 'all_days'] + [str(i) for i in range(1, 31)]


class TimeRange(TypedDict):
    since: str
    until: str

class FacebookExplainedError(Exception):
    pass


class FacebookInsight(object):
    """" represents one line of the AdAccount Insight Report """

    PROPERTIES = AVAILABLE_FIELDS + AVAILAIBLE_BREAKDOWNS

    def __init__(self, **kwargs):
        unexpected_keys = set(kwargs.keys()) - set(FacebookInsight.PROPERTIES)
        if unexpected_keys:
            warnings.warn(f"Keys {', '.join(sorted(unexpected_keys))} are unexpected for FacebookInsight object")
            for key in unexpected_keys:
                kwargs.pop(key)
        self.__dict__.update(kwargs)


class FacebookQueryArg(object):
    def __init__(self,
                 fields : List[str],
                 breakdowns: List[str] = None,
                 level: str = 'adset',
                 date_preset: Optional[str] = 'last_30d',
                 filtering: List[Dict] = None,
                 time_increment: str = '1',
                 use_account_attribution_setting: bool = False,
                 time_range: Optional[TimeRange] = None):

        self.fields = [field for field in fields if field in AVAILABLE_FIELDS]
        if breakdowns is None:
            breakdowns = []

        self.params = {'breakdowns': [breakdown for breakdown in breakdowns if breakdown in AVAILAIBLE_BREAKDOWNS],
                       'level': level if level in ['ad', 'adset', 'campaign', 'account'] else 'adset',
                       'filtering': filtering if filtering else [],
                       'time_increment': time_increment if time_increment in AVAILABLE_TIME_INCREMENTS else '1',
                       'use_account_attribution_setting': use_account_attribution_setting}
        if time_range:
            self.params['time_range'] = time_range
        else:
            self.params['date_preset'] = date_preset if date_preset in AVAILABLE_DATE_PRESET else 'last_30d'

    def to_dict(self):
        return dict(params=self.params, fields=self.fields)

    def get_sorted_column_names(self):
        return sorted([field for field in self.fields] + [breakdown for breakdown in self.params['breakdowns']])

@backoff.on_exception(backoff.expo, (FacebookRequestError), max_tries=10)
def get_facebook_report(fb_account_id: str, facebook_credentials: str, fb_query_args: FacebookQueryArg) -> List[FacebookInsight]:
    with open(facebook_credentials) as credentials:
        facebook_credentials_dict = json.load(credentials)

    FacebookAdsApi.init(access_token=facebook_credentials_dict['access_token'])

    account = AdAccount('act_' + fb_account_id)
    excpt = None
    i_async_job: AdReportRun = None
    # Insights
    for retry_number, error_sleep_time in enumerate([1, 2, 4, 6]):
        # len(--) == retry_number // value in array == interval_between_retry

        try:
            i_async_job: AdReportRun = account.get_insights_async(fields=fb_query_args.to_dict()['fields'],
                                                                  params=fb_query_args.to_dict()['params'])
            break
        except FacebookRequestError as e:
            excpt = e
            if str(e.api_error_subcode()) == '1487742':  # too many calls from this ad-account.
                logging.info(f'waiting {error_sleep_time}s for retry number {retry_number + 1}')
                time.sleep(error_sleep_time)
            else:
                break
    if isinstance(excpt, FacebookRequestError):
        raise FacebookExplainedError(f'type: {excpt.api_error_type()}'
                                     f'message: {excpt.api_error_message()},'
                                     f'http status code: {excpt.http_status()},'
                                     f'api code: {excpt.api_error_code()},'
                                     f'api subcode: {excpt.api_error_subcode()},'
                                     f'api blame_field_specs: {excpt.api_blame_field_specs()}')
    elif excpt is not None:
        raise excpt
    start = time.time()
    while True:
        try:
            job = i_async_job.api_get()
            job_status = str(job[AdReportRun.Field.async_status])
            job_completion = str(job[AdReportRun.Field.async_percent_completion])
            logging.info("Prepare Report : " + job_status + " - " + job_completion + "%")
            if (job[AdReportRun.Field.async_percent_completion] >= 100 and job[AdReportRun.Field.async_status] == 'Job Completed'):
                break
            elif job[AdReportRun.Field.async_status] == 'Job Failed':
                raise Exception(f"Job execution Failed")
            else:
                time.sleep(5)
        except FacebookRequestError as e:
            if str(e.api_error_subcode()) == '99':  # An unknown error occurred.
                raise FacebookExplainedError(
                    f'type: {excpt.api_error_type()}'
                    f'message: {excpt.api_error_message()},'
                    f'http status code: {excpt.http_status()},'
                    f'api code: {excpt.api_error_code()},'
                    f'api subcode: {excpt.api_error_subcode()},'
                    f'api blame_field_specs: {excpt.api_blame_field_specs()}'
                )
            raise e

    insights = i_async_job.get_result(params=dict(limit=1000))
    end = time.time()
    logging.info(f'Preparation took {end-start} seconds.')
    logging.info(f"Preparation completed for Facebook report, account {fb_account_id}. Starting report download...")

    start = time.time()
    insights_list = [FacebookInsight(**insight) for insight in insights]
    end = time.time()
    logging.info(f'Download took {end-start} seconds.')
    return insights_list


def check_access_by_getting_account_data(fb_account_id, facebook_credentials):
    """
        Check access by trying to retrieve account_data

        Return:
            account:Facebook object account
            account_name:string

        Raises:
            FacebookAccountLostAccessException : when no access to the account
    """

    with open(facebook_credentials) as credentials:
        facebook_credentials = json.load(credentials)

    try:
        FacebookAdsApi.init(access_token=facebook_credentials['access_token'])
        account = AdAccount('act_' + str(fb_account_id))
        account_data = account.api_get(fields=[AdAccount.Field.name])
        account_name = account_data["name"]
    except FacebookRequestError:
        raise FacebookAccountLostAccessException(f'Could not access account {fb_account_id}. Are you sure you entered the correct id and granted access?')

    return account, account_name
