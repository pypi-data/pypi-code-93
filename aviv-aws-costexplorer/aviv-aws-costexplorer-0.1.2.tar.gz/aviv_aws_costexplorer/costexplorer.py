"""
Helper class to retrieve AWS CAU

See: https://github.com/aws-samples/aws-cost-explorer-report/blob/master/src/lambda.py

"""
import os
import logging
import datetime
from dateutil.relativedelta import relativedelta
from . import (
    base,
    types
)

log = logging.getLogger(__name__)

AWS_CE_REQUESTID = os.environ.get('AWS_CE_REQUESTID', '0')

class CostExplorer(base.AWSClient):
    __granularity: types.CAUGranularity = None
    __period: types.CAUTimePeriod = None
    __metrics: types.CAUMetrics = None

    def __init__(
            self,
            *,
            role_arn: str=None,
            granularity: types.CAUGranularity='MONTHLY',
            metrics: types.CAUMetrics=['UnblendedCost', 'BlendedCost'],
            period: relativedelta=None,
            date: datetime.datetime=None) -> None:
        """
        Helper to build an AWS Cost Explorer report (sets of CAU calls)

        Args:
            granularity (GranularityTypes, optional): [description]. Defaults to 'MONTHLY'.
            period (relativedelta, optional): [description]. Defaults to None.
            date (datetime.datetime, optional): [description]. Defaults to None.
            client (botocore.client.BaseClient, optional): [description]. Defaults to None.
        """
        super().__init__()
        self.ce = self.client('ce', role_arn=role_arn)
        self.granularity = granularity.upper()
        self.__metrics = metrics
        self._setup_period(date=date, period=period)

    @property
    def period(self) -> types.CAUTimePeriod:
        return self.__period

    @property
    def metrics(self) -> types.CAUMetrics:
        return self.__metrics

    @property
    def granularity(self) -> types.CAUGranularity:
        return self.__granularity

    @granularity.setter
    def granularity(self, val: types.CAUGranularity):
        self.__granularity = val.upper()

    def _setup_period(self, date: datetime.datetime=None, period: relativedelta=None) -> None:
        """Set granularity, period and start, end time for which we're going to query CE

        Args:
            date (datetime.date, optional): Date until when we want to have costs (end). Defaults to datetime.date.today().
            period (relativedelta, optional): Time period for which we want data. Defaults to 1 click of 'Granularity', ex: 1month, 1day, etc...
        """
        if not date:
            date = datetime.datetime.today()
        if not period:
            period = types.CAUDefaultPeriods[self.granularity]

        # Do full month collection *until* 01/MM/YYYY to end of month (calculated with diff from period)
        if self.granularity == 'HOURLY':
            date = date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc)
            date_df = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            if self.granularity == 'MONTHLY':
                date = date.replace(day=1)
            date_df = lambda d: d.strftime("%Y-%m-%d")
        self.__period = dict(
            Start=date_df((date - relativedelta(**period))),
            End=date_df(date)
        )
        log.info(f"Start:{self.period['Start']} / End:{self.period['End']} / Granularity: {self.granularity}")

    def get_cost_and_usage(self, **props: types.CostAndUsageAttributes) -> dict:
        """Recursively query CE to get cost (and usage) data

        Note: no there is no boto3 paginator for ce.get_cost_and_usage :(

        Args:
            Granularity (GranularityTypes, optional): [description]. Defaults to 'MONTHLY'.
            TimePeriod (typing.Dict[typing.Literal[, optional): [description]. Defaults to None.
            Filter (CAUFilter, optional): [description]. Defaults to None.
            Metrics (CAUMetrics, optional): [description]. Defaults to ['UnblendedCost', 'BlendedCost'].
            GroupBy (list, optional): [description]. Defaults to None.
            NextPageToken (str, optional): [description]. Defaults to None.
        Returns:
            dict: AWS Cost Explorer CAU api call response
        """
        if 'TimePeriod' not in props:
            props['TimePeriod'] = self.period
        if 'Granularity' not in props:
            props['Granularity'] = self.granularity
        if 'Metrics' not in props:
            props['Metrics'] = self.metrics

        log.info(f"get_cost_and_usage({props})")
        response = self.ce.get_cost_and_usage(**props)
        data = response['ResultsByTime']
        log.debug(f" >> Req:{response['ResponseMetadata']['RequestId']} - {sum(len(d['Groups']) for d in data)} records")
        # Query and append additional data
        while 'NextPageToken' in response:
            props['NextPageToken'] = response['NextPageToken']
            response = self.ce.get_cost_and_usage(**props)
            if AWS_CE_REQUESTID == "1":
                for rtb in response['ResultsByTime']:
                    rtb['RequestId'] = response['ResponseMetadata']['RequestId']
            data += response['ResultsByTime']
            log.debug(f" -> Req:{response['ResponseMetadata']['RequestId']} - {sum(len(d['Groups']) for d in data)} records")
        response['ResultsByTime'] = data
        return response

    def get_tags(self, TagKey: str, SearchString: str='', TimePeriod: dict=None) -> dict:
        """
        Get the list a valid tags (over a given period)
        """
        if not TimePeriod:
            TimePeriod={
                'Start': self.period['Start'][0:10],
                'End': self.period['End'][0:10]
            }
        return self.ce.get_tags(
            TimePeriod=TimePeriod,
            TagKey=TagKey,
            SearchString=SearchString
        )
