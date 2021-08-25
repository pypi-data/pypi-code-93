from dotenv import load_dotenv
load_dotenv()
import os


def meraki_api_key():
    meraki_api_key = os.getenv('meraki_api_key', None)
    if meraki_api_key is None:
        raise SystemExit('Please set environment variable meraki_api_key')
    else:
        meraki_api_key = os.environ['meraki_api_key']
    return (meraki_api_key)


def meraki_organization_id():
    meraki_organization_id = os.getenv('meraki_organization_id', None)
    if meraki_organization_id is None:
        raise SystemExit('Please set environment variable meraki_organization_id')
    else:
        meraki_organization_id = os.environ['meraki_organization_id']
    return (meraki_organization_id)

def meraki_base_url():
    meraki_base_url = os.getenv('meraki_base_url', None)
    if meraki_base_url is None:
        raise SystemExit('Please set environment variable meraki_base_url')
    else:
        meraki_base_url = os.environ['meraki_base_url']
    return (meraki_base_url)
