from typing import Tuple
from awsee.sessioninfo import CallerIdentity
from awsee.messages import Messages
import boto3
from awsee.general import *
from dateutil import tz
from datetime import timedelta, tzinfo
from awsee.logmanager import LogManager
from awsee.style import Style
from awsee.utils import Utils
from awsee.preferences import Preferences
from botocore.exceptions import ClientError


class AwsServices:

    def __init__(self):
        self.preferences = Preferences()

    def botoSession(self, profile):
        if not profile:
           return boto3.Session()
        return boto3.Session(profile_name=profile)

    def getAccountOwner(self, profile=None):
        sts = self.botoSession(profile).client("sts")
        return sts.get_caller_identity()

    def getMFADevices(self, profile=None):
        iam = self.botoSession(profile).client("iam")
        return iam.list_mfa_devices()

    def botoSessionWithToken(self, stsToken):
        session = boto3.session.Session(
            aws_access_key_id=stsToken['Credentials']['AccessKeyId'],
            aws_secret_access_key=stsToken['Credentials']['SecretAccessKey'],
            aws_session_token=stsToken['Credentials']['SessionToken']
        )
        return session
    
    def startSessionWithTokenAndAssumeRole(self, _stsToken, roleArn) -> Tuple[dict, dict]:
        stsToken = self.botoSessionWithToken(_stsToken).client('sts').assume_role(
            RoleArn=roleArn,
            RoleSessionName="mysession",
            DurationSeconds=self.preferences.durationSeconds
        )
        callerIdentity = self.getCallerIdentity(stsToken)
        self._convertsUTCDateExpirationToLocaZoneDate(stsToken)
        return stsToken, callerIdentity


    def assumeRole(self, roleArn, profile=None, mfaSerial=None, mfaToken=None) -> Tuple[dict, dict]:
        try:
            stsToken       = None
            callerIdentity = None
            if mfaSerial and mfaToken:
                # In case a MFA Token is necessary to assume the role
                stsToken = self.botoSession(profile).client('sts').assume_role(
                    RoleArn=roleArn,
                    RoleSessionName="mysession",
                    DurationSeconds=self.preferences.durationSeconds,
                    SerialNumber=mfaSerial,
                    TokenCode=mfaToken
                )
            else:
                # In case the active AWS Session does not need a MFA Role 
                stsToken = self.botoSession(profile).client('sts').assume_role(
                    RoleArn=roleArn,
                    RoleSessionName="mysession",
                    DurationSeconds=self.preferences.durationSeconds
                )
            callerIdentity = self.getCallerIdentity(stsToken)
        except ClientError as e:
            if e.response['Error']['Code'] == "AccessDenied":
                msg = e.response['Error']['Message']
                if not mfaSerial:
                    mfaSerial = ""
                Messages.showError("Access Denied!",f"{msg}\n    {mfaSerial}")
                return None, None
            else:
                print(e.response['Error']['Code'])
                raise e
        self._convertsUTCDateExpirationToLocaZoneDate(stsToken)
        return stsToken, callerIdentity


    def _convertsUTCDateExpirationToLocaZoneDate(self, stsToken):
        localDate = Utils.parseUTCDateToLocalZoneDate(stsToken["Credentials"]["Expiration"])
        stsToken["Credentials"]["Expiration"] = localDate

    def getCallerIdentity(self, _stsToken):
        try:
            callerIdentity = self.botoSessionWithToken(_stsToken)  \
                                  .client('sts').get_caller_identity()
            return callerIdentity
        except ClientError as e:
            if e.response['Error']['Code'] == "AccessDenied":
                msg = e.response['Error']['Message']
                Messages.showError("Access Denied!",f"{msg}")
                return None
            else:
                print(e.response['Error']['Code'])
                raise e

    def getSessionToken(self, mfaSerial, mfaToken, profile=None) -> Tuple[dict, dict]:
        try:
            session = self.botoSession(profile)
            stsToken = session.client('sts').get_session_token(
                DurationSeconds=self.preferences.durationSeconds,
                SerialNumber=mfaSerial,
                TokenCode=mfaToken,
            )
            callerIdentity = self.getCallerIdentity(stsToken)
        except ClientError as e:
            if e.response['Error']['Code'] == "AccessDenied":
                msg = e.response['Error']['Message']
                Messages.showError("Access Denied!",f"{msg}\n    {mfaSerial}")
                return None, None
            else:
                print(e.response['Error']['Code'])
                raise e
        self._convertsUTCDateExpirationToLocaZoneDate(stsToken)
        return stsToken, callerIdentity
        
        # For Temporary Tests
        # stsToken = {
        #     "AccessKeyId": "ASIAV7NRRSDFSFFGGQSP24HZ",
        #     "SecretAccessKey": "QXsks0IQyTnS9qkUntDtrukfsldhyfnwlefGB8ztFZ7",
        #     "SessionToken": "FwoGZXIvYXdzEJ3//////////wEaDDVEVIvDLPKruvdC4CKFAQ7hnQi0eWG7pjprKnsmFNAnvgMtP4foPy6KygfDcBrEExJdWxnL0S4ok=",
        #     "Expiration": datetime.datetime.now()
        # }
        # return stsToken

        
        
