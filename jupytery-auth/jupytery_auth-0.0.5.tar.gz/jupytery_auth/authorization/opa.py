import json
import os
import requests


OPA_HOST = os.environ.get('OPA_ADDR', 'http://localhost:8181')
OPA_POLICY_PATH = os.environ.get('OPA_POLICY_PATH', '/v1/data/httpapi/authz')
OPA_URL = OPA_HOST + OPA_POLICY_PATH

def check_opa_authorization(user, action, resource):
    input_dict = {
        "input": {
            'user': user['login'],
            'action': action,
            'resource': resource,
            'hireable': user['hireable'],
            'token': user['jwt_token'],
        }
    }
    try:
        opa_rsp = requests.post(OPA_URL, data = json.dumps(input_dict))
    except Exception as err:
        print(err)
        return {}
    if opa_rsp.status_code >= 300:
        print("Error checking authorization, got status %s and message: %s" % (opa_rsp.status_code, opa_rsp.text))
        return {}
    rsp = opa_rsp.json()
#    print(f"Authorization response for {user['login']}, {action}, {resource}: {json.dumps(rsp, indent=2)}")
    return rsp
