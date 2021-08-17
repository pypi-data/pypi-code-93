import configparser

"""
https://blog.gruntwork.io/authenticating-to-aws-with-the-credentials-file-d16c0fbcbf9e

$ aws configure
AWS Access Key ID: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-west-2
Default output format [None]: json

AWS prompts you to enter your Access Key ID and Secret Access Key and stores them in ~/.aws/credentials:

[default]
aws_access_key_id=AKIAIOSFODNN7EXAMPLE
aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

It also stores the other settings you entered in ~/.aws/config:

[default]
region=us-west-2
output=json
"""


async def gather(hub):
    """
    load profiles from unencrypted AWS credential files

    Example:
    .. code-block:: yaml

        aws.iam:
            paths:
                - ~/.aws/credentials
                - /path/to/other/credential/file
            # Optional overrides
            id: XXXXXXXXXXXXXXXXX
            key: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            region: us-east-1
    """
    sub_profiles = {}
    config = configparser.ConfigParser()

    ctx = hub.acct.PROFILES.get("aws.iam", {})
    credential_files = ctx.pop("paths", [])
    config.read(credential_files)

    for profile in set(config.sections()):
        # Let boto do it's magic to figure out all the profile stuff based on the name
        sub_profiles[profile] = ctx

    return sub_profiles
