import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import Session
from typing import Any, Dict, List
import os
import requests
import json
import zipfile

retry_strategy = Retry(
    total=2,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "PUT", "POST", "DELETE", "OPTIONS", "TRACE"],
)

retry_adapter = HTTPAdapter(max_retries=retry_strategy)
requests_retry = Session()
requests_retry.mount("https://", retry_adapter)
requests_retry.mount("http://", retry_adapter)
tempdir_ttl_days = 1


def assert_valid_name(name: str):
    is_valid = re.match(r"^[A-Za-z0-9_]+$", name)
    if not is_valid:
        raise Exception(
            f"'{name}' must only contain alphanumeric and underscore characters."
        )


def raise_resp_exception_error(resp):
    if not resp.ok:
        message = None
        try:
            r_body = resp.json()
            message = r_body.get("message") or r_body.get("msg")
        except:
            # If we failed for whatever reason (parsing body, etc.)
            # Just return the code
            if resp.status_code == 500:
                raise Exception(
                    f"HTTP Error received: {resp.reason}: {str(resp.status_code)}"
                )
            else:
                raise Exception(
                    f"HTTP Error received: {resp.reason}: {str(resp.status_code)} | {resp.json()['detail']}"
                )
        if message:
            raise Exception(f"Error: {message}")
        else:
            if resp.status_code == 500:
                raise Exception(
                    f"HTTP Error received: {resp.reason}: {str(resp.status_code)}"
                )
            else:
                raise Exception(
                    f"HTTP Error received: {resp.reason}: {str(resp.status_code)} | {resp.json()['detail']}"
                )


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def _upload_local_files(
    file_names: List[str],
    get_upload_path: str,
    headers: Dict[str, Any],
    upload_prefix: str,
    upload_suffix: str,
    delete_after_upload: bool = True,
):
    """
    This uploads a set of files in batches with a reader.

    Args:
        file_names (str): The local file_names (files to be uploaded)
        get_upload_path (str): The URL that generates upload URLs
        headers (Dict[str, Any]): Headers for the get_upload_path request
        upload_prefix (str): Prefix for the filepath (once uploaded)
        upload_suffix (str): Suffix for the filepath (once uploaded)
        delete_after_upload (bool): Whether to delete the file after upload

    Return:
        A list of download URLs for the uploaded files
    """
    xml_api_headers = {
        "content-type": "application/octet-stream",
    }

    download_urls = []
    if len(file_names) == 0:
        return download_urls

    url_chunks = chunks(file_names, 100)

    param_batch_list = []
    for i, chunk in enumerate(url_chunks, start=1):
        for count, file_name in enumerate(chunk, start=1):

            upload_filename, ext = os.path.splitext(os.path.basename(file_name))

            param_batch_list.append(
                {"file_name": upload_filename, "file_extension": ext}
            )

            if count == len(chunk):

                data = {"files": param_batch_list}

                upload_urls_resp = requests_retry.post(
                    get_upload_path,
                    headers=headers,
                    data=json.dumps(data).encode("utf-8"),
                )
                raise_resp_exception_error(upload_urls_resp)
                batch_of_urls = upload_urls_resp.json()
                param_batch_list = []
        # batch_of_urls comes back in the same expected order as the chunk, so we zip and enumerate simultaneously.
        for count, (file_name, urlobj) in enumerate(zip(chunk, batch_of_urls), start=1):
            with open(file_name, "rb") as f:
                files = {"file": (file_name, f)}
                http_response = requests.post(
                    urlobj["url"], data=urlobj["fields"], files=files
                )

    return True


def _upload_local_zip(
    zip_filepath: str,
    get_upload_path: str,
    complete_upload_path: str,
    headers: Dict[str, Any],
    upload_prefix: str,
    upload_suffix: str,
    delete_after_upload: bool = True,
):
    """This uploads a set of files in batches with a reader.

    Args:
        file_names (str): The local file_names (files to be uploaded)
        get_upload_path (str): The URL that generates upload URLs
        headers (Dict[str, Any]): Headers for the get_upload_path request
        upload_prefix (str): Prefix for the filepath (once uploaded)
        upload_suffix (str): Suffix for the filepath (once uploaded)
        delete_after_upload (bool): Whether to delete the file after upload

    Return:
        A list of download URLs for the uploaded files
    """
    xml_api_headers = {
        "content-type": "application/octet-stream",
    }

    download_urls = []

    upload_filename, ext = os.path.splitext(os.path.basename(zip_filepath))

    max_size = 1 * 1024 ** 3  # 5GB is max, we use 1GB
    zip_size = os.path.getsize(zip_filepath)
    parts_no = zip_size // max_size + 1
    num_files = len(zipfile.ZipFile(zip_filepath).namelist())
    payload = {"parts": parts_no, "num_files": num_files}

    upload_url_parts_resp = requests_retry.get(
        get_upload_path, headers=headers, params=payload
    )

    raise_resp_exception_error(upload_url_parts_resp)
    upload_id = upload_url_parts_resp.json()[0]
    batch_of_urls = upload_url_parts_resp.json()[1]

    parts = []
    with open(zip_filepath, "rb") as fin:
        for num, url in enumerate(batch_of_urls):
            part = num + 1
            file_data = fin.read(max_size)

            res = requests.put(url, data=file_data)
            # Should this raise an Exception instead of just returning?
            if res.status_code != 200:
                return
            etag = res.headers["ETag"]
            parts.append({"ETag": etag, "PartNumber": part})

    data = {"parts": parts}

    comp_resp = requests_retry.post(
        complete_upload_path + "/" + upload_id,
        headers=headers,
        data=json.dumps(data).encode("utf-8"),
    )

    return {"status_code": comp_resp.status_code, "data": comp_resp.json()}


def validate_dataservices_args(**kwargs):
    less_than_equal_one = ["momentum", "adam_eps", "weight_decay", "factor"]

    if kwargs["early_stop_patience"] > kwargs["num_epochs"]:
        raise ValueError(
            f"'early_stop_patience' is {kwargs['early_stop_patience']} and must be equal to or less than 'num_epochs' which is {kwargs['num_epochs']}."
        )

    for arg_name, arg_value in kwargs.items():
        # Checking int/float values
        if type(arg_value) is int or type(arg_value) is float:
            if arg_name in less_than_equal_one:
                if arg_value < 0 or arg_value > 1:
                    raise ValueError(
                        f"{arg_name} is {arg_value} and must be between 0-1."
                    )

            if arg_value < 0:
                raise ValueError(
                    f"{arg_name} is {arg_value} and must be equal to or greater than 0."
                )
        # Checking tuple values
        if type(arg_value) is tuple:
            for num in arg_value:
                if num < 0:
                    raise ValueError(
                        f"{arg_name} is {arg_value} and must have values equal to or greater than 0."
                    )
