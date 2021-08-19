# from IPython.core.display import display_javascript, Javascript

import requests

from trifacta.util.tfconfig import read_config

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/83.0.4103.97 Safari/537.36",
}


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "Bearer " + self.token
        return r


def get_config(filepath: str = None):
    if filepath is None:
        config, config_exist = read_config()
    else:
        config, config_exist = read_config(filepath)
    if not config_exist:
        raise PermissionError(
            "You must setup a trifacta configuration, use tfconfig.setup_configuration(user, pwd)"
        )

    return config


def get_endpoint() -> str:
    return get_config()["endpoint"]


def get_auth() -> BearerAuth:
    config = get_config()
    # return HTTPBasicAuth(config['username'], config['password'])
    return BearerAuth(config["token"])


def check_success(r: requests.request):
    if r.status_code >= 400:

        try:
            error = r.json()
        except:
            error = r.text
        raise Exception("An error occurred while executing the request", error)


def raw_get(url: str, params=None) -> requests.request:
    auth, endpoint = get_auth(), get_endpoint()
    r = requests.get(endpoint + url, params, auth=auth, headers=headers)
    return r


def get(url: str, params=None) -> requests.request:
    r = raw_get(url, params)
    check_success(r)
    return r


def post(url: str, data=None, json=None, files=None, headers=None) -> requests.request:
    auth, endpoint = get_auth(), get_endpoint()
    r = requests.post(
        endpoint + url, data=data, json=json, files=files, headers=headers, auth=auth
    )
    check_success(r)
    return r


def delete(url: str, headers=None) -> requests.request:
    auth, endpoint = get_auth(), get_endpoint()
    r = requests.delete(endpoint + url, headers=headers, auth=auth)
    check_success(r)
    return r


def put(url: str, data=None, json=None) -> requests.request:
    auth, endpoint = get_auth(), get_endpoint()
    r = requests.put(endpoint + url, data=data, json=json, headers=headers, auth=auth)
    check_success(r)
    return r


def patch(url: str, data=None, json=None) -> requests.request:
    auth, endpoint = get_auth(), get_endpoint()
    r = requests.patch(endpoint + url, data=data, json=json, headers=headers, auth=auth)
    check_success(r)
    return r


def upload(url, filename, file) -> requests.request:
    auth, endpoint = get_auth(), get_endpoint()
    r = requests.post(endpoint + url, files={"file": (filename, file)}, auth=auth)
    check_success(r)
    return r


# not currently needed
def download_vfs(uri):
    r = get(f"/readVfsFile?uri={uri}")
    return r
