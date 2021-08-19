#!/usr/bin/env python3
copyright = 'copyright 2021 r.kras'
import argparse
import json
import os
import socket
import sys
from urllib.parse import urlencode
import webbrowser

import boto3
import requests

version_info=f'{sys.argv[0]}  0.1 {copyright}'

# role defaults
role_template='arn:aws:iam::{account}:role/{rolename}'
def_role_name='DefaultConsoleRole'
def_duration=3600

# STS and Console URLS
aws_signin_url = 'https://signin.aws.amazon.com/'
aws_signin_url = 'https://signin.aws.amazon.com/federation'
aws_console_url = 'https://console.aws.amazon.com/'

verbose = False

def arg_parse():
    """ Parse command arguments """

    global def_role_name

    parser = argparse.ArgumentParser(description='Open AWS Console in a Browser',
        epilog='\n'+ ('-'*25))
    
    def_prof = os.environ.get('AWS_PROFILE','default')

    if env_role_name := os.environ.get('AWS_ROLE_ARN'):
        def_role_name = env_role_name.split('/')[-1]
    
    def_name = os.environ.get('AWS_ROLE_SESSION_NAME', f'{os.getlogin()}-{socket.gethostname()}')
    
    parser.add_argument('-V', '--version', help='Print version and exit.', action='store_true')
    parser.add_argument('-v', '--verbose', help=f'Verbose output [{verbose}]', action='store_true')
    parser.add_argument('-p', '--profile', help=f'Specify AWS profile [{def_prof}]', default=None)
    parser.add_argument('-o', '--output', help='Only Print the URL [False]', action='store_true')
    parser.add_argument('-a', '--assume-role', help='Assume role first [False]', action='store_true')
    parser.add_argument('-s', '--short-role-name', help=f'Specify role name to assume [{def_role_name}]', default=def_role_name)
    parser.add_argument('-r', '--role-arn', help=f'(optonal) full arn to assume [{env_role_name}]', default=env_role_name)
    parser.add_argument('-n', '--name', help=f'Session name for assume role [{def_name}]', default=def_name)
    parser.add_argument('-d', '--duration', help=f'Specify session duration [{def_duration} Sec]', default=def_duration, type=int)

    args = parser.parse_args()

    return args


def eprint(*args, **kwargs):
    """Print errors to stderr."""
    print(*args, **kwargs, file=sys.stderr)


def vprint(*args, **kwargs):
    """ Print verbose to stderr """
    if verbose:
        print(*args, **kwargs, file=sys.stderr)


# This is not used
def get_session_token(args):
    """ Get and return temporary credentials. """
 
    if args.profile:
        prof = {'profile_name': args.profile}
    else:
        prof = {}   # Let boto3 sort it out

    sts = boto3.session.Session(**prof).client('sts')
 
    ret = sts.get_session_token(DurationSeconds=args.duration)

    if not 'Credentials' in ret:
        vprint('Error: getting session token', ret)
        raise Exception('STS: GetSessionToken failed')
    
    return { # return format for sts sigin.aws.amazon.com/federation
            'sessionId': ret['Credentials']['AccessKeyId'],
            'sessionKey': ret['Credentials']['SecretAccessKey'],
            'sessionToken': ret['Credentials']['SessionToken']
        }


def get_credentials(args):
    """ Return current or assumed role credentials """
    
    sess = boto3.session.Session(profile_name=args.profile)
    sts = sess.client('sts')

    # Find out who we are
    ret = sts.get_caller_identity()
    if not 'Account' in ret:
        raise Exception('STS: Get Caller Identity failed')
    
    account_id = ret['Account']

    # Check if we are federated or already assumed a role
    if svc := ret['Arn'].split(':')[2] == 'sts':
        # Already federated or have assumed a role
        current_creds = sess.get_credentials()
        if args.assume_role:
            # As users explicitly selected --assume_role - we error out
            emsg = f'Error: Current Session "{current_creds.method}" can not assume role'
            vprint(emsg)
            raise Exception(emsg)
        else:
            # Federated user or assumed role uses current credentials
            vprint(f'Session is already "{current_creds.method}" - reusing these credentials')
            return {
                'sessionId': current_creds.access_key,
                'sessionKey': current_creds.secret_key,
                'sessionToken': current_creds.token
            }
    
    # this is an iam user - assume provided or default role and use those credentials
    if args.role_arn:
        # provided a full ARN (e.g. cross-account)
        role_to_assume = args.role_arn
    else:
        # provided short or no role name - create the ARN
        role_name = args.short_role_name or def_role_name
        role_to_assume = role_template.format(account=account_id, rolename=role_name)

    ret = sts.assume_role(
        RoleArn = role_to_assume,
        RoleSessionName = args.name,
        DurationSeconds = args.duration,
    )

    if not 'Credentials' in ret:
        vprint('Error: Assuming Role', ret)
        raise Exception('STS: Assume role failed')
    
    vprint(f'role {role_to_assume} has been assumed.')
    return { # return format for sts sigin.aws.amazon.com/federation
            'sessionId': ret['Credentials']['AccessKeyId'],
            'sessionKey': ret['Credentials']['SecretAccessKey'],
            'sessionToken': ret['Credentials']['SessionToken']
        }
    

def request_signin_token(args, session_creds):
    """ Create URL requesting signin token """
    args = {
        'Action': 'getSigninToken',
        'SessionDuration': args.duration,
        'Session': json.dumps(session_creds)
    }
    url = aws_signin_url + '?' + urlencode(args, doseq=True)  
    return url


def request_console_login(sin_token):
    """ Creating URL requesting signed console login. """

    args = {
        'Action': 'login',
        'Issuer': socket.gethostname(),
        'Destination': aws_console_url,
        'SigninToken': sin_token
    }
    return aws_signin_url + '?' + urlencode(args, doseq=True,)# quote_via=quote)


def get_console_url(args):
    """ Get a console login URL """

    # Get credentials, maybe assume the role
    session_creds = get_credentials(args)
    
    #  build the token request and fetch the sign-in token
    url = request_signin_token(args, session_creds)

    r = requests.get(url,timeout=200.0)
    if r.status_code != 200:
        vprint('Error: Getting SigninToken', r.url)
        vprint(r.content)
        raise Exception(f'Bad response requesting signin token {r.reason}')
    
    sin_token = r.json()['SigninToken']

    # build the console signin url
    sin_url = request_console_login(sin_token)

    if args.output:
        return sin_url
    else:
        vprint(f'Opening webbrowser for {sin_url}')
        webbrowser.open(sin_url)
        return None


def consurl():
    
    args = arg_parse()
    if args.verbose:
        verbose = True
        vprint('verbose mode enabled')
    
    if args.version:
        print(version_info, file=sys.stdout)
    else:
        try:    
            url = get_console_url(args)
            if url:
                print(url, file=sys.stdout)

        except Exception as e:
            if verbose:
                raise e
            eprint(e)

if __name__ == '__main__':
    consurl()