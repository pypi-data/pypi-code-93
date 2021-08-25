import boto3
import botocore.client
import datetime
from dateutil.relativedelta import relativedelta
from .costexplorer import CostExplorer, CAUProps, CostExplorerFilter, DimensionsKeys
from .base import AWSClient



class AWSBudgets(AWSClient):
    def __init__(self) -> None:
        super().__init__()
        self.client = self.assume_role_client(client_type='budgets')


    def get_budgets(self) -> list:
        """List AWS (Billing) budgets set on an AWS account

        Returns:
            list: budgets
        """
        data = self.client.describe_budgets(AccountId=self.account_id)
        if 'Budgets' not in data:
            return []
        # Flatten and extend, a bit (see: stamp_record) results
        for record in data['Budgets']:
            record.update(self._flatten_amounts(record))
            if 'CalculatedSpend' in record:
                record.update(self._flatten_amounts(record['CalculatedSpend']))
                del record['CalculatedSpend']
            if 'CostTypes' in record:
                record.update(record['CostTypes'])
                del record['CostTypes']
            if 'CostFilters' in record:
                # record.update(record['CostTypes'])
                del record['CostFilters']

            self.stamp_record(record, data['ResponseMetadata'])
            record['CheckDate'] = str(datetime.date.today())
            # Fix date formating inconsistancy with timezones
            for datestamp in ['LastUpdatedTime', 'Start', 'End']:
                if datestamp in record and record[datestamp]:
                    record[datestamp] = record[datestamp].isoformat()
        return data['Budgets']
