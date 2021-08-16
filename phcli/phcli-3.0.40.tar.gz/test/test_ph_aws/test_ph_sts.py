import boto3
from phcli.ph_aws.ph_sts import PhSts


def test_ph_sts_assume_role():
    credentials = PhSts().assume_role('arn:aws-cn:iam::444603803904:role/Ph-Cli-Lmd', 'Ph-Cli-Lmd').get_cred()
    assert credentials is not None
    s3_client = boto3.client('s3', **credentials)
    assert s3_client.list_buckets() is not None
