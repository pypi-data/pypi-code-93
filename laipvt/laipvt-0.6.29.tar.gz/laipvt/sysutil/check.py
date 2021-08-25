import os
from laipvt.sysutil.gvalue import LAIPVT_BASE_DIR, CHECK_FILE, PRE_CHECK_RESULT_FILE
from laipvt.sysutil.util import get_yaml_config

def is_pre_check():
    try:
        if os.path.exists(LAIPVT_BASE_DIR) and os.path.exists(CHECK_FILE) and os.path.exists(PRE_CHECK_RESULT_FILE):
            check_context = get_yaml_config(PRE_CHECK_RESULT_FILE)
            # print(check_context)
            if check_context["total"]:
                return True
        return False
    except Exception as e:
        return False


def check_use_https_ca():
    try:
        check_info = get_yaml_config(CHECK_FILE)

        if check_info["deploy_https"]:
            if not check_info["self_signed_ca"]:
                if not os.path.exists(check_info["ca_crt_path"]) and not os.path.exists(check_info["ca_key_path"]):
                    return False
        return True
    except Exception as e:
        return False

def check_https_ca_self_signed():
    try:
        check_info = get_yaml_config(CHECK_FILE)
        if check_info["self_signed_ca"]:
            return True
    except Exception as e:
        return False