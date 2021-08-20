import json
import re
from typing import Dict, Optional, List, Iterable

import boto3
import requests
from retry import retry

import montecarlodata.settings as settings
from montecarlodata.common.data import MonolithResponse
from montecarlodata.errors import manage_errors, complain_and_abort, abort_on_gql_errors


class Wrapper:
    def __init__(self, abort_on_error: Optional[bool] = True):
        self._abort_on_error = abort_on_error


class GqlWrapper(Wrapper):
    def __init__(self, mcd_id: str, mcd_token: str):
        self._mcd_id = mcd_id
        self._mcd_token = mcd_token
        self._endpoint = settings.MCD_API_ENDPOINT

        super().__init__()

    def make_request(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a GraphQl request to the MCD API. Aborts on error if set.
        """
        response = self._make_request(query=query, variables=variables)
        if response:
            if self._abort_on_error and response.get('errors'):
                complain_and_abort(response['errors'])
            return response['data']

    def make_request_v2(self, query: str, operation: str, variables: Optional[Dict] = None) -> MonolithResponse:
        """
        Make a GraphQl request to the MCD API and parse out the results into data and errors. Aborts on error if set.
        """
        response = self._make_request(query=query, variables=self.convert_snakes_to_camels(variables))
        parsed_response = MonolithResponse(data=response.get('data', {}).get(operation), errors=response.get('errors'))

        if self._abort_on_error:
            abort_on_gql_errors(parsed_response)
        return parsed_response

    @staticmethod
    def convert_snakes_to_camels(dict_: Dict) -> Dict:
        """
        Converts dictionary keys from snake_case to camelCase as Gql is very opinionated
        """
        return {re.sub(r'_([a-z])', lambda x: x.group(1).upper(), k): v for k, v in dict_.items()}

    @manage_errors
    def _make_request(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        headers = {'x-mcd-id': self._mcd_id, 'x-mcd-token': self._mcd_token, 'Content-Type': 'application/json'}
        payload = {'query': query, 'variables': variables or {}}

        if settings.MCD_USER_ID_HEADER:
            headers = {'user-id': settings.MCD_USER_ID_HEADER}  # override for local development

        response = self._post(headers=headers, payload=payload)
        response.raise_for_status()

        return json.loads(response.text)

    @retry(tries=3, delay=0.2, backoff=2, max_delay=1)
    def _post(self, headers: Dict, payload: Dict) -> requests.request:
        return requests.post(self._endpoint, json=payload, headers=headers)


class AwsClientWrapper(Wrapper):
    _CF_CREATE_WAITER = 'stack_create_complete'
    _CF_UPDATE_WAITER = 'stack_update_complete'
    _DEFAULT_WAITER_CONFIG = {'Delay': 5, 'MaxAttempts': 720}
    _DEFAULT_CAPABILITIES = 'CAPABILITY_IAM'
    _STACK_CREATE_STATE = 'CREATE_COMPLETE'
    _STACK_UPDATE_STATE = 'UPDATE_COMPLETE'
    # Map from the shorthand state form available in the AWS CLI to the actual states.
    _EMR_STATES = {
        'active': ['STARTING', 'BOOTSTRAPPING', 'RUNNING', 'WAITING', 'TERMINATING'],
        'terminated': ['TERMINATED'],
        'failed': ['TERMINATED_WITH_ERRORS']
    }

    def __init__(self, profile_name: Optional[str] = None, region_name: Optional[str] = None,
                 session: Optional[boto3.session.Session] = None):
        super().__init__()

        self._session = session or self._get_session(profile_name=profile_name, region_name=region_name)
        self._test_if_region_is_set()

    @manage_errors
    def get_stack_details(self, stack_id: str) -> Dict:
        """
        Retrieve stack details (description) from DC
        """
        return self._session.client('cloudformation').describe_stacks(StackName=stack_id)

    @manage_errors
    def get_stack_outputs(self, stack_id: str) -> Dict:
        """
        Convenience utility to retrieve stack outputs from DC
        """
        return self.get_stack_details(stack_id)['Stacks'][0]['Outputs']

    @manage_errors
    def get_stack_parameters(self, stack_id: str) -> List[Dict]:
        """
        Convenience utility to retrieve stack parameters from the DC
        """
        return self.get_stack_details(stack_id)['Stacks'][0].get('Parameters')

    @manage_errors
    def create_stack(self, stack_name: str, template_link: str, termination_protection: bool,
                     parameters: Optional[List[Dict]] = None) -> bool:
        """
        Attempts to deploy the DC stack - returning True on success
        """
        deployment_options = dict(
            StackName=stack_name,
            TemplateURL=template_link,
            Capabilities=[self._DEFAULT_CAPABILITIES],
            EnableTerminationProtection=termination_protection
        )
        if parameters:
            deployment_options['Parameters'] = parameters

        response = self._session.client('cloudformation').create_stack(**deployment_options)
        stack_id = response['StackId']
        return self._wait_on_stacks(stack_id=stack_id, waiter=self._CF_CREATE_WAITER,
                                    success_state=self._STACK_CREATE_STATE)

    @manage_errors
    def upgrade_stack(self, stack_id: str, template_link: str, parameters: List[Dict]) -> bool:
        """
        Attempts to upgrade the DC stack - returning True on success
        """
        self._session.client('cloudformation').update_stack(StackName=stack_id, TemplateURL=template_link,
                                                            Capabilities=[self._DEFAULT_CAPABILITIES],
                                                            Parameters=parameters)
        return self._wait_on_stacks(stack_id=stack_id, waiter=self._CF_UPDATE_WAITER,
                                    success_state=self._STACK_UPDATE_STATE)

    @manage_errors
    def deploy_gateway(self, gateway_id: str, stage: Optional[str] = 'prod') -> None:
        """
        Attempts to deploy the DC gateway
        """
        self._session.client('apigateway').create_deployment(restApiId=gateway_id, stageName=stage)

    @manage_errors
    def upload_file(self, bucket_name: str, object_name: str, file_path: str) -> None:
        """
        Upload a file to s3://bucket/object from file path
        """
        self._session.client('s3').upload_file(file_path, bucket_name, object_name)

    @manage_errors
    def create_role(self, role_name: str, trust_policy: str, tags: Optional[List] = None) -> str:
        """
        Creates an IAM role and returns the ARN on success
        """
        return self._session.client('iam').create_role(RoleName=role_name,
                                                       AssumeRolePolicyDocument=trust_policy, Tags=tags)['Role']['Arn']

    @manage_errors
    def attach_inline_policy(self, role_name: str, policy_name: str, policy_doc: str) -> str:
        """
        Attaches an inline policy to an existing role
        """
        return self._session.client('iam').put_role_policy(RoleName=role_name, PolicyName=policy_name,
                                                           PolicyDocument=policy_doc)

    @manage_errors
    def get_emr_cluster_details(self, created_after: Optional[str] = None, states: Optional[List] = None
                                ) -> Iterable[Dict]:
        """
        Retrieves details of all EMR clusters
        """
        client = self._session.client('emr')
        params = {}
        if created_after:
            params['CreatedAfter'] = created_after
        if states:
            params['ClusterStates'] = [mapped for state in states for mapped in self._EMR_STATES[state]]
        pages = client.get_paginator('list_clusters').paginate(**params)
        for page in pages:
            for cluster in page['Clusters']:
                yield client.describe_cluster(ClusterId=cluster['Id']).get('Cluster')

    @manage_errors
    def _test_if_region_is_set(self) -> None:
        """
        Test if region is set by creating a client. Abort on failure
        """
        self._session.client('cloudformation')  # throws NoRegion if not set

    @manage_errors
    def _get_session(self, profile_name: str, region_name: str) -> Optional[boto3.session.Session]:
        """
        Create a session using named profile/region if set. Uses AWS defaults if not set.
        """
        session_args = (('profile_name', profile_name), ('region_name', region_name))
        return boto3.session.Session(**{k: v for k, v in session_args if v})  # throws ProfileNotFound if invalid

    def _wait_on_stacks(self, stack_id: str, waiter: str, success_state: str) -> bool:
        """
        Wait for stack to finish operation
        """
        self._session.client('cloudformation').get_waiter(waiter).wait(StackName=stack_id,
                                                                       WaiterConfig=self._DEFAULT_WAITER_CONFIG)
        return self.get_stack_details(stack_id)['Stacks'][0]['StackStatus'] == success_state
