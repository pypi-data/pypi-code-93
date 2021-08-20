import json
import secrets
import time
from typing import Optional, Dict, Iterable, List

import click
from tabulate import tabulate

from montecarlodata.common.user import UserService
from montecarlodata.config import Config
from montecarlodata.errors import complain_and_abort, manage_errors
from montecarlodata.utils import AwsClientWrapper


class CloudResourceService:
    _MCD_ROLE_PREFIX = 'monte-carlo-integration-role'
    _MCD_POLICY_PREFIX = 'monte-carlo-integration-cli-policy'
    _MCD_TAGS = [{'Key': 'MonteCarloData', 'Value': ''}]
    _LIST_EMR_FRIENDLY_HEADERS = ['Name', 'Id', 'State', 'LogUri']

    def __init__(self, config: Config, user_service: Optional[UserService] = None,
                 aws_wrapper: Optional[AwsClientWrapper] = None, aws_profile_override: Optional[str] = None,
                 aws_region_override: Optional[str] = None):

        self._abort_on_error = True

        self._user_service = user_service or UserService(config=config)
        self._aws_wrapper = aws_wrapper or AwsClientWrapper(profile_name=aws_profile_override or config.aws_profile,
                                                            region_name=aws_region_override or config.aws_region)

    @manage_errors
    def create_role(self, path_to_policy_doc: str) -> None:
        """
        Creates a DC compatible role from the provided policy doc
        """
        current_time = str(time.time())
        external_id = self._generate_random_token()
        role_name = f'{self._MCD_ROLE_PREFIX}-{current_time}'
        policy_name = f'{self._MCD_POLICY_PREFIX}-{current_time}'

        try:
            policy = json.dumps(self._read_json(path_to_policy_doc))

            # use the AWS account id of collector, which may not necessarily be account id running the CLI
            account_id = self._user_service.active_collector['customerAwsAccountId']
        except json.decoder.JSONDecodeError as err:
            complain_and_abort(f'The provided policy is not valid JSON - {err}')
        except KeyError as err:
            complain_and_abort(f'Missing expected property ({err}). The collector may not have been deployed before')
        else:
            trust_policy = self._generate_trust_policy(account_id=account_id, external_id=external_id)
            role_arn = self._aws_wrapper.create_role(role_name=role_name, trust_policy=trust_policy, tags=self._MCD_TAGS)
            click.echo(f"Created role with ARN - '{role_arn}' and external id - '{external_id}'.")

            self._aws_wrapper.attach_inline_policy(role_name=role_name, policy_name=policy_name, policy_doc=policy)
            click.echo(f'Success! Attached provided policy.')

    @staticmethod
    def _generate_trust_policy(account_id: str, external_id: str) -> str:
        """
        Generates a DC compatible trust policy
        """
        return json.dumps(
            {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Effect': 'Allow',
                        'Principal': {
                            'AWS': f'arn:aws:iam::{account_id}:root'
                        },
                        'Action': 'sts:AssumeRole',
                        'Condition': {
                            'StringEquals': {
                                'sts:ExternalId': external_id
                            }
                        }
                    }
                ]
            }
        )

    @staticmethod
    def _generate_random_token(length: Optional[int] = 16) -> str:
        """
        Generates a random token (e.g. for the external id)
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def _read_json(path: str) -> Dict:
        """
        Reads a JSON file from the path.
        """
        with open(path) as file:
            return json.load(file)  # loads for the purpose of validating

    @manage_errors
    def list_emr_clusters(self, only_log_locations: Optional[bool] = False, created_after: Optional[str] = None,
                          states: Optional[List] = None, no_grid: Optional[bool] = False,
                          headers: Optional[str] = 'firstrow', table_format: Optional[str] = 'fancy_grid'):
        """
        Displays information about EMR cluster (name, id, state and log location). If only_log_locations is True,
        displays a deduplicated list of EMR log locations.
        """
        clusters = self._aws_wrapper.get_emr_cluster_details(created_after=created_after, states=states)
        if only_log_locations:
            self._list_emr_clusters_only_log_locations(clusters)
        elif no_grid:
            self._list_emr_clusters_details_no_wait(clusters)
        else:
            self._list_emr_cluster_details(clusters, headers=headers, table_format=table_format)

    def _list_emr_cluster_details(self, clusters: Iterable[Dict], headers: Optional[str] = 'firstrow',
                                  table_format: Optional[str] = 'fancy_grid'):
        rows = [
            self._emr_details_row(cluster) for cluster in clusters if cluster
        ]
        click.echo(tabulate([self._LIST_EMR_FRIENDLY_HEADERS] + rows, headers=headers, tablefmt=table_format))

    def _list_emr_clusters_details_no_wait(self, clusters: Iterable[Dict]):
        """
        Display information row by row, used when it can take long to wait for all data to format the table.
        """
        found = False
        for cluster in clusters:
            if not cluster:  # Should never happen.
                continue
            found = True
            # Prints line by line to show progress as the list may be long.
            click.echo(tabulate([self._emr_details_row(cluster)], tablefmt='plain'))
        if not found:
            click.echo(f'No clusters found')

    @staticmethod
    def _list_emr_clusters_only_log_locations(clusters: Iterable[Dict]):
        log_locations = set()
        for cluster in clusters:
            if not cluster:  # Should never happen.
                continue
            log_locations.add(cluster.get('LogUri'))
        if not log_locations:
            click.echo(f'No clusters found')
        else:
            for location in log_locations:
                click.echo(location)

    @staticmethod
    def _emr_details_row(cluster: Dict) -> List[str]:
        return [cluster['Name'], cluster['Id'], cluster['Status']['State'], cluster.get('LogUri')]
