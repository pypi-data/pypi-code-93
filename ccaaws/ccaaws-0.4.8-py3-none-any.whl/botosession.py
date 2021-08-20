"""Base Module for creating a default session with boto3 to AWS"""
import boto3
import ccalogging

log = ccalogging.log


class NoCreds(Exception):
    pass


class BotoSession:
    """Base class to create a default boto3 session"""

    def __init__(self, **kwargs):
        """sets up a default connection to AWS.

        will use the default setting from your credentials file unless
        either the profile or accessid/secretkey are supplied.

        Keyword Arguments:
            profile - the ~/.aws/credentials profile to use.
            accesskey - the aws access key id to use (along with the secret key).
            secretkey - the aws secret access key to use (along with the access key id).
            stoken - the aws session token to use
            region - the aws region

        Environment Variables (if set override the default credentials):
            AWS_ACCESS_KEY_ID
            AWS_SECRET_ACCESS_KEY
            AWS_SESSION_TOKEN
        """
        self.client = None
        self.noresource = False
        self.profile = None
        self.region = None
        self.usekeys = False
        self.kwargs = None
        self.usedefault = True
        if "noresource" in kwargs:
            self.noresource = True
            del kwargs["noresource"]
        if "region" in kwargs:
            self.region = kwargs["region"]
            del kwargs["region"]
        if "profile" in kwargs:
            self.profile = kwargs["profile"]
            del kwargs["profile"]
        if len(kwargs) > 0:
            if "accesskey" in kwargs and "secretkey" in kwargs:
                self.kwargs = {}
                if self.region is not None:
                    self.kwargs["region_name"] = self.region
                self.kwargs["aws_access_key_id"] = kwargs["accesskey"]
                self.kwargs["aws_secret_access_key"] = kwargs["secretkey"]
                if "stoken" in kwargs:
                    self.kwargs["aws_session_token"] = kwargs["stoken"]
                self.usekeys = True
                self.usedefault = False
                # access keys override profiles
                self.profile = None
            else:
                emsg = "Incomplete credentials supplied"
                raise NoCreds(emsg)

    def newSession(self):
        if self.profile is None:
            if self.region is None:
                return boto3.session.Session()
            else:
                return boto3.session.Session(region_name=self.region)
        else:
            if self.region is None:
                return boto3.session.Session(profile_name=self.profile)
            else:
                return boto3.session.Session(
                    profile_name=self.profile, region_name=self.region
                )

    def newClient(self, service="iam"):
        try:
            if self.usekeys:
                if self.region is None:
                    self.client = boto3.client(service, **self.kwargs)
            else:
                session = self.newSession()
                self.client = session.client(service)
                if not self.noresource:
                    self.resource = session.resource(service)
        except Exception as e:
            msg = "Failed to create a {} client. {}: {}".format(
                service, type(e).__name__, e
            )
            log.error(msg)
            raise NoCreds(msg)
        return self.client
