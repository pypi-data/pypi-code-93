"""aws-lp main"""
from __future__ import print_function, unicode_literals

import base64
import logging
import sys
from os import environ
from builtins import input
from getpass import getpass

from lastpass_aws_login import credentials
from lastpass_aws_login.conf import init
from lastpass_aws_login.exceptions import (LastPassCredentialsError, LastPassError,
                               LastPassIncorrectOtpError)
from lastpass_aws_login.lastpass import LastPass
from lastpass_aws_login.utils import binary_type, get_saml_aws_roles

from threadlocal_aws.clients import sts

logging.basicConfig(
    format='[%(asctime)s][%(name)s][%(levelname)s]: %(message)s',
    stream=sys.stdout)
LOGGER = logging.getLogger(__name__)


def main():
    """Log into LastPass, get SAML auth, assume role, and write tokens into credentials file"""
    conf = init()

    if conf.VERBOSE:
        logging.getLogger('lastpass_aws_login').setLevel(logging.DEBUG)


    username = None
    # Get the federated credentials from the user
    if not conf.NO_PROMPT:
        sys.stdout.write("Username [" + conf.DEFAULT_USERNAME + "]: ")
        username = input()
    if not username:
        if conf.DEFAULT_USERNAME:
            username = conf.DEFAULT_USERNAME
        else:
            print("Need to give username")
            sys.exit(1)
    otp = None
    if "LASTPASS_DEFAULT_PASSWORD" in environ and environ["LASTPASS_DEFAULT_PASSWORD"]:
        password = environ["LASTPASS_DEFAULT_PASSWORD"]
    else:
        password = getpass()
    if "LASTPASS_DEFAULT_OTP" in environ and environ["LASTPASS_DEFAULT_OTP"]:
        otp = environ["LASTPASS_DEFAULT_OTP"]


    username = binary_type(username)
    password = binary_type(password)
    lastpass_session = LastPass('https://lastpass.com')

    try:
        lastpass_session.login(username, password, otp=otp)
    except LastPassIncorrectOtpError:
        mfa = input('MFA: ')

        try:
            lastpass_session.login(username, password, otp=mfa)
        except LastPassIncorrectOtpError:
            sys.exit('Invalid MFA code')
    except LastPassCredentialsError:
        sys.exit('Invalid username or password')
    except LastPassError as error:
        # don't display stack trace but still exit and print error message
        sys.exit(str(error))

    assertion = lastpass_session.get_saml_token(conf.SAML_ID)

    awsroles = get_saml_aws_roles(base64.b64decode(assertion))
    # Overwrite and delete the credential variables, just for safety
    username = "##############################################"
    password = "##############################################"
    del username
    del password
    role_arn = None
    if conf.NO_PROMPT and conf.ROLE_ARN:
        for awsrole in awsroles:
            if awsrole.startswith(conf.ROLE_ARN + ","):
                role_arn = conf.ROLE_ARN
                principal_arn = awsrole.split(",")[1]
        if not role_arn:
           role_arn, principal_arn = select_role(awsroles)
    else:
        # If I have more than one role, ask the user which one they want,
        # otherwise just proceed
       role_arn, principal_arn = select_role(awsroles)

    if not role_arn:
        print("No valid role found in assertions")
        print(awsroles)
        sys.exit(3)
    # Use the assertion to get an AWS STS token using Assume Role with SAML
    token = sts().assume_role_with_saml(
        RoleArn=role_arn,
        PrincipalArn=principal_arn,
        SAMLAssertion=assertion,
        DurationSeconds=conf.DURATION,
    )
    credentials.write(token, conf.PROFILE)

def select_role(awsroles):
    role_arn = None
    principal_arn = None
    if len(awsroles) > 1:
        i = 0
        print("Please choose the role you would like to assume:")
        for awsrole in awsroles:
            print("[" + str(i) + "]: " + awsrole.split(",")[0])
            i += 1
        sys.stdout.write("Selection: ")
        selectedroleindex = input()

        # Basic sanity check of input
        if int(selectedroleindex) > (len(awsroles) - 1):
            print("You selected an invalid role index, please try again")
            sys.exit(1)

        role_arn = awsroles[int(selectedroleindex)].split(",")[0]
        principal_arn = awsroles[int(selectedroleindex)].split(",")[1]
    elif awsroles:
        role_arn = awsroles[0].split(",")[0]
        principal_arn = awsroles[0].split(",")[1]
    return role_arn, principal_arn
