import os
import logging
import datetime
from dateutil.relativedelta import relativedelta
from . import (
    costexplorer,
    types
)

AWS_CE_ACCOUNTID = os.environ.get('AWS_CE_ACCOUNTID', '0')
AWS_CE_AMOUNTUNIT = os.environ.get('AWS_CE_AMOUNTUNIT', '0')

log = logging.getLogger(__name__)


class CostReporter(costexplorer.CostExplorer):
    def __init__(
            self,
            *,
            role_arn: str=None,
            granularity: str='MONTHLY',
            period: relativedelta=None,
            date: datetime.datetime=None) -> None:
        """Aviv AWS Cost Reporter

        Args:
            role_arn (str, optional): [description]. Defaults to None.
            granularity (str, optional): [description]. Defaults to 'MONTHLY'.
            period (relativedelta, optional): [description]. Defaults to None.
            date (datetime.datetime, optional): [description]. Defaults to None.
        """
        super().__init__(
            role_arn=role_arn,
            granularity=granularity,
            period=period,
            date=date
        )

    # Data manipulations
    @staticmethod
    def flatten_amounts(amounts: dict) -> dict:
        """Transform the CAU Metrics amount from a nested dict
          {METRIC1: {"Amount": 42, "Unit": "USD"}, METRIC2...}
          to a flat one.

        Args:
            amounts (dict): Total of Metrics dict from CAU record

        Returns:
            dict: Amounts keyd by metric name
        """
        flats = {}
        for a, v in amounts.items():
            flats[a] = v['Amount']
            if AWS_CE_AMOUNTUNIT:
                flats[f"{a}Unit"] = v['Unit']
        return flats

    @staticmethod
    def extend_groups(record: dict, group_definitions: list=None) -> list:
        """Returns a flat list (array) of records from CAU response with groupby(s)

        Args:
            record (dict): a record/element of a CAU ResultsByTime
            group_definitions (list, optional): [description]. Defaults to None.

        Returns:
            list: exploded records from CAU response results
        """
        groups = record['Groups'].copy()
        del record['Groups']
        records = list()
        for group in groups:
            g = record.copy()
            for group_pos, group_def in enumerate(group_definitions):
                if group_def['Type'] in g:
                    g[group_def['Type']] += ',' + group_def['Key']
                else:
                    g[group_def['Type']] = group_def['Key']
                g[group_def['Key']] = group['Keys'][group_pos]
            g.update(CostReporter.flatten_amounts(group['Metrics']))
            records.append(g)
        return records

    def _stamp_record(self, record: dict, metadata: dict) -> None:
        """Augment record with meta information about what was collected.

        Args:
            record (dict): the record to augment
            metadata (dict): information about the API request (ResponseMetadata)
        """
        if AWS_CE_ACCOUNTID == "1":
            # Save where the CAU query was made
            record['AccountId'] = self.account_id
        # Specific to cost_and_usage (CAU)
        record['Granularity'] = self.granularity
        # Save TimePeriod + RequestId
        if 'TimePeriod' in record:
            record.update(record['TimePeriod'])
            del record['TimePeriod']
            record['Period'] = record['Start'].replace('-', '')
            if self.granularity == 'MONTHLY':
                record['Period'] = record['Period'][0:6]
            elif self.granularity == 'DAILY':
                record['Period'] = record['Period'][0:8]

    # Calls to AWS CAU api
    def get_cost_and_usage(self, **props: types.CostAndUsageAttributes) -> list:
        """Calls underlying CostExplorer.get_cost_and_usage to produce CAU records

        This method will also:
         - Extend and flatten the response ['ResultsByTime'], see: _extend_flatten_cau_record method
         - Cleanup extra ['ResponseMetadata']

        Args:
            Granularity (GranularityTypes, optional): [description]. Defaults to 'MONTHLY'.
            TimePeriod (typing.Dict[typing.Literal[, optional): [description]. Defaults to None.
            Filter (CAUFilter, optional): [description]. Defaults to None.
            Metrics (CAUMetrics, optional): [description]. Defaults to ['UnblendedCost', 'BlendedCost'].
            GroupBy (list, optional): [description]. Defaults to None.
            NextPageToken (str, optional): [description]. Defaults to None.

        Returns:
            list: The CAU records
        """
        data = super().get_cost_and_usage(**props)

        # Process results, turn them into a list of flat dicts
        records = list()
        for record in data['ResultsByTime']:
            self._stamp_record(record, data['ResponseMetadata'])
            if 'Total' in record:
                record.update(CostReporter.flatten_amounts(record['Total']))
                del record['Total']

            #'GroupDefinitions' in data and data['GroupDefinitions']:
            if 'Groups' in record and record['Groups']:
                records += CostReporter.extend_groups(record, data['GroupDefinitions'])
            else:
                if 'Groups' in record:
                    del record['Groups']
                records.append(record)

        self._cau_info(data, records)
        return records

    # Devel
    def _cau_info(self, resp: dict, records):
        log.info(f"Got CAU {len(resp['ResultsByTime'])} resppoints for {resp.keys()}")

        if len(resp['ResultsByTime']) < len(records):
            log.info(f"Extended from {len(resp['ResultsByTime'])} to {len(records)} datapoints")

        if 'GroupDefinitions' in resp and resp['GroupDefinitions']:
            log.info(f"- GroupDefinitions:{resp['GroupDefinitions']}")
        if 'DimensionValueAttributes' in resp and resp['DimensionValueAttributes']:
            log.info(f"- DimensionValueAttributes:{resp['DimensionValueAttributes']}")
