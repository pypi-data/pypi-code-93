import pan.xapi
import pan.commit
import paloalto_env
import sys


def xapi_con(key=None, device_ip=None):
    if not key:
        key = paloalto_env.paloalto_api_key()
    if not device_ip:
        device_ip = paloalto_env.paloalto_panorama_ip()
    xapi = pan.xapi.PanXapi(api_key=key, hostname=device_ip)
    return xapi


def xapi_set(xapi, set_list):
    try:
        xapi.set(xpath=set_list[0], element=set_list[1])
        # .override as an alternative
    except pan.xapi.PanXapiError as PE:
        print(PE)
        sys.exit(1)


def xapi_op(xapi, command):
    try:
        xapi.op(cmd=command)
    except pan.xapi.PanXapiError as PE:
        print(PE)
        sys.exit(1)


def xapi_commit(xapi):
    c = pan.commit.PanCommit(validate=False, force=False, commit_all=False, merge_with_candidate=False)
    # ajouter serial
    cmd = c.cmd()
    xapi.commit(cmd=cmd)
