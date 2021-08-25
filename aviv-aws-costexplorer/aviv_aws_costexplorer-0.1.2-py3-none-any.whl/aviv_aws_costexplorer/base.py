import logging
import botocore.client
import boto3
import boto3.session

class AWSClient():
    _sts: botocore.client.BaseClient = None

    def __init__(self) -> None:
        pass

    @property
    def sts(self) -> botocore.client.BaseClient:
        if not self._sts:
            self._sts = self.client('sts')
        return self._sts

    @property
    def account_id(self) -> str:
        """Returns the AWS Account ID we're connected to (boto3 client/session)

        Returns:
            str: AWS Account ID
        """
        return self.sts.get_caller_identity()['Account']

    def assume_role(self, role_arn: str, role_session_name: str='AssumeRole') -> dict:
        """Use AWS STS to AssumeRole and get temporary credentials

        Args:
            role_arn (str): [description]
            role_session_name (str, optional): [description]. Defaults to 'AssumeRole'.

        Returns:
            dict: [description]
        """
        resp = self.sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=role_session_name
        )
        return AWSClient.sts_credentials(resp)

    def session(
            self,
            *,
            role_arn: str=None,
            role_session_name: str='Session',
            set_as_detault: bool=False,
            **kwargs) -> boto3.session.Session:
        """Creates a boto3 session

        Args:
            role_arn (str, optional): Assume this IAM role first
            role_session_name (str, optional): Assumed role session name. Defaults to 'Session'.
            set_as_detault (bool, optional): Set session as boto3

        kwargs: Additionnal arguments for boto3.sessions.Session
            region_name (str): AWS Region
            profile_name: AWS Profile
            botocore_session: re-use boto3 session

        Returns:
            boto3.session.Session: [description]
        """
        if role_arn:
            kwargs.update(self.assume_role(role_arn, role_session_name))
        session = boto3.session.Session(**kwargs)
        if set_as_detault:
            logging.warning(f"Setting default boto3 session: {role_session_name} for {role_arn}")
            boto3.DEFAULT_SESSION = session
        return session

    def client(
            self,
            type: str,
            *,
            role_arn: str=None,
            role_session_name: str='Session',
            **kwargs) -> botocore.client.BaseClient:
        """Create a boto3 client to a specific AWS service API

        Args:
            role_arn (str, optional): Assume this IAM role first
            role_session_name (str, optional): Assumed role session name. Defaults to 'Session'.

        kwargs: Additionnal arguments for boto3.client
            region_name (str): AWS Region

        Returns:
            botocore.client.BaseClient: [description]
        """
        if role_arn:
            kwargs.update(self.assume_role(role_arn, role_session_name))
        return boto3.client(type, **kwargs)

    @staticmethod
    def sts_credentials(resp: dict) -> dict:
        """Transform AWS sts.assume_role API response to a boto3-compatible dict with credentials

        Args:
            resp (dict): AWS sts.assume_role response

        Raises:
            KeyError: If response doesn't have any 'Credentials'

        Returns:
            dict: with aws_access_key_id/aws_secret_access_key/aws_session_token
        """
        if "Credentials" not in resp:
            raise KeyError("Credentials not found (check sts response?)")
        credentials = resp["Credentials"]
        creds = {}
        if 'AccessKeyId' in credentials:
            creds['aws_access_key_id'] = credentials["AccessKeyId"]
        if 'SecretAccessKey' in credentials:
            creds['aws_secret_access_key'] = credentials["SecretAccessKey"]
        if 'SessionToken' in credentials:
            creds['aws_session_token'] = credentials["SessionToken"]
        return creds
