"""
Helping to test s3
"""
import contextlib
import copy
import os

from moto import mock_s3
import boto3
from botocore.utils import fix_s3_host
import six
from six.moves import urllib


@contextlib.contextmanager
def modified_environment_variables(**kwargs):
    kwargc = copy.deepcopy(kwargs)
    old_envvars = {k: os.environ.get(k)
                   for k in six.viewkeys(kwargc) &
                   six.viewkeys(dict(os.environ))}
    for k, v in kwargc.items():
        os.environ[k] = v
    yield
    for k, v in kwargc.items():
        try:
            oldv = old_envvars[k]
            os.environ[k] = oldv
        except KeyError as e:
            del os.environ[k]


@contextlib.contextmanager
def mock_s3_session_resource_bucket(
        bucketname="testbucket", sessionparams={}, resourceparams={}):
    with mock_s3():
        sess = boto3.session.Session(**sessionparams)
        res = sess.resource('s3', **resourceparams)
        # res.meta.client.meta.events.unregister(
        #     "before-sign.s3", fix_s3_host)

        res.create_bucket(Bucket=bucketname)

        yield sess, res, bucketname


@contextlib.contextmanager
def mock_s3_base_uri(
        bucketname="testbucket", sessionparams={}, resourceparams={},
        include_query=True):
    envvars = {
        "AWS_ACCESS_KEY_ID": "testing",
        "AWS_SECRET_ACCESS_KEY": "testing",
        "AWS_SECURITY_TOKEN": "testing",
        "AWS_SESSION_TOKEN": "testing"
    }

    with modified_environment_variables(**envvars):
        with mock_s3_session_resource_bucket(
                bucketname, sessionparams, resourceparams) as (sess, res, b):

            # verify s3 bucket i/o
            buck = res.Bucket(b)
            mybucketmsg = "hello world"
            mymsgkey = "mytestmsg"
            buck.put_object(Key=mymsgkey, Body=mybucketmsg.encode("UTF-8"))

            msg = res.Object(bucketname, mymsgkey).get()["Body"].read().decode("UTF-8")
            assert msg == mybucketmsg

            paramstring = (urllib.parse.urlencode({
                "profile_name": sess.profile_name,
                "region_name": res.meta.client.meta.region_name,
                "endpoint_url": res.meta.client.meta.endpoint_url,
            }) if include_query else '')

            yield urllib.parse.urlunparse(urllib.parse.ParseResult(
                "s3", b, "/", "", paramstring, ""))





# instead of testing with parameters, maybe just test marshalling in here
