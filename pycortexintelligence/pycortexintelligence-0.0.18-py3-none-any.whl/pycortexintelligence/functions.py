import datetime

import requests

from pycortexintelligence.core.messages import *

LOADMANAGER = "https://api.cortex-intelligence.com"


def _make_url_auth(plataform_url):
    return "https://{}/service/integration-authorization-service.login".format(plataform_url)


def _make_download_url(plataform_url):
    return 'https://{}/service/integration-cube-service.download?'.format(plataform_url)


def _get_sid_bearer_token(auth_endpoint, credentials):
    """
    :param auth_endpoint:
    :param credentials:
    :return:
    """
    response = requests.post(auth_endpoint, json=credentials)
    response_json = response.json()
    return {"Authorization": "Bearer " + response_json["key"]}


def _get_data_input(content, loadmanager, headers):
    """
    :param content:
    :param loadmanager:
    :param headers:
    :return:
    """
    endpoint = loadmanager + "/datainput"
    response = requests.post(endpoint, headers=headers, json=content)
    data_input_id = response.json()["id"]
    return data_input_id


def _get_execution_id(data_input_id, content, loadmanager, headers):
    """
    :param data_input_id:
    :param content:
    :param loadmanager:
    :param headers:
    :return:
    """
    endpoint = "{}/datainput/{}/execution".format(loadmanager, data_input_id)
    response = requests.post(endpoint, headers=headers, json=content)
    execution_id = response.json()["executionId"]
    return execution_id


def _start_process(execution_id, loadmanager, headers):
    """
    :param execution_id:
    :param loadmanager:
    :param headers:
    :return:
    """
    endpoint = loadmanager + "/execution/" + execution_id + "/start"
    response = requests.put(endpoint, headers=headers)
    return response


def _execution_history(execution_id, loadmanager, headers):
    """
    :param execution_id:
    :param loadmanager:
    :param headers:
    :return:
    """
    endpoint = loadmanager + "/execution/" + execution_id  # + '/history'
    response = requests.get(endpoint, headers=headers)
    return response


def upload_file_to_cube(cubo_id,
                        file_like_object,
                        auth_endpoint,
                        credentials,
                        loadmanager=LOADMANAGER,
                        data_format={
                            "charset": "UTF-8",
                            "quote": "\"",
                            "escape": "\\",
                            "delimiter": ",",
                            "fileType": "CSV"
                        },
                        timeout={
                            'file': 300,
                            'execution': 600,
                        },
                        execution_parameters={
                            'name': 'LoadManager PyCortex',
                        },
                        datainput_parameters={
                            'ignoreValidationErrors': False
                        }
                        ):
    """
    :param timeout:
    :param cubo_id:
    :param file_like_object:
    :param auth_endpoint:
    :param credentials:
    :param loadmanager:
    :param data_format:
    :return:
    """

    # ================ Get Bearer Token ===================
    headers = _get_sid_bearer_token(auth_endpoint, credentials)

    # ================ Content ============================
    content = {
        "destinationId": cubo_id,
        'ignoreValidationErrors': datainput_parameters['ignoreValidationErrors'],
        "fileProcessingTimeout": int(timeout['file']),
        "executionTimeout": int(timeout['execution']),
    }

    # ================ Get Data Input Id ======================
    data_input_id = _get_data_input(content, loadmanager, headers)

    # ================ Get Execution Id =======================
    execution_id = _get_execution_id(data_input_id, execution_parameters, loadmanager, headers)

    # ================ Send files =============================
    endpoint = loadmanager + "/execution/" + execution_id + "/file"
    response = requests.post(
        endpoint,
        headers=headers,
        data=data_format,
        files={"file": file_like_object},
    )

    # ================ Start Data Input Process ===========================
    _start_process(execution_id, loadmanager, headers)

    return execution_id, headers


def upload_to_cortex(**kwargs):
    """
    :param cubo_id:
    :param file_path:
    :param plataform_url:
    :param username:
    :param password:
    :param data_format: data_format={
                            "charset": "UTF-8",
                            "quote": "\"",
                            "escape": "\\",
                            "delimiter": ",",
                            "fileType": "CSV"
                        }
    :param timeout: {
        'file': 300,
        'execution': 600,
    }
    :param loadmanager: LOADMANAGER
    :return:
    """
    # Read Kwargs
    cubo_id = kwargs.get('cubo_id')
    file_path = kwargs.get('file_path')
    plataform_url = kwargs.get('plataform_url')
    username = kwargs.get('username')
    password = kwargs.get('password')
    file_like_object = kwargs.get('file_like_object')
    if not file_path and not file_like_object:
        raise ValueError(INVALID_FILES_ERROR, f'FORAM PASSADOS: {file_path}, {file_like_object}')
    if not file_like_object:
        file_like_object = open(file_path, "rb")

    data_format = kwargs.get('data_format', {
        "charset": "UTF-8",
        "quote": "\"",
        "escape": "\\",
        "delimiter": ",",
        "fileType": "CSV"
    })
    timeout = kwargs.get('timeout', {
        'file': 300,
        'execution': 600,
    })
    loadmanager = kwargs.get('loadmanager', LOADMANAGER)
    execution_parameters = kwargs.get('execution_parameters', {
        'name': 'LoadManager PyCortex',
    })
    datainput_parameters = kwargs.get('datainput_parameters', {
        'ignoreValidationErrors': False
    })

    if 'file' not in timeout.keys() and 'execution' not in timeout.keys():
        raise ValueError(FORMAT_TIMEOUT)

    # Verify Kwargs
    if cubo_id and file_like_object and plataform_url and username and password:
        auth_endpoint = _make_url_auth(plataform_url)
        credentials = {"login": str(username), "password": str(password)}
        execution_id, headers = upload_file_to_cube(
            cubo_id=cubo_id,
            file_like_object=file_like_object,
            auth_endpoint=auth_endpoint,
            credentials=credentials,
            data_format=data_format,
            timeout=timeout,
            loadmanager=loadmanager,
            execution_parameters=execution_parameters,
            datainput_parameters=datainput_parameters,
        )
        response = _execution_history(execution_id, LOADMANAGER, headers)
        return response
    else:
        raise ValueError(ERROR_ARGUMENTS_VALIDATION)


def download_from_cortex(**kwargs):
    """
    :param cubo_id:
    :param cubo_name:
    :param plataform_url:
    :param username:
    :param password:
    :param columns:
    :param file_path:
    :param data_format:
    :param filters:
    :return:
    """
    cubo_id = kwargs.get('cubo_id')
    cubo_name = kwargs.get('cubo_name')
    plataform_url = kwargs.get('plataform_url')
    username = kwargs.get('username')
    password = kwargs.get('password')
    columns = kwargs.get('columns')
    file_path = kwargs.get('file_path')
    data_format = kwargs.get('data_format', {
        "charset": "UTF-8",
        "quote": "\"",
        "escape": "\\",
        "delimiter": ",",
    })
    filters = kwargs.get('filters', None)
    if cubo_id and cubo_name:
        raise ValueError(DOWNLOAD_ERROR_JUST_ID_OR_NAME)
    if (cubo_id or cubo_name) and plataform_url and username and password and columns and file_path:
        # Verify is a ID or Name
        if cubo_id:
            cube = '{"id":"' + cubo_id + '"}'
        else:
            cube = '{"name":"' + cubo_name + '"}'

        # Columns to Download
        columns_download = []
        for column in columns:
            columns_download.append({
                "name": column,
            })
        columns_download = str(columns_download).replace("'", '"')

        # Need to Apply Filters
        if filters:
            filters_download = []
            for filter in filters:
                column_name = filter[0]
                value = filter[1]
                element = {
                    "name": column_name,
                    "type": "SIMPLE",
                }
                try:
                    value = datetime.datetime.strptime(value, "%d/%m/%Y")
                    element["type"] = "DATE"
                    element["rangeStart"] = value.strftime("%Y%m%d")
                    element["rangeEnd"] = value.strftime("%Y%m%d")
                except ValueError:
                    value_temp = value
                    try:
                        value = value.split('-')
                        date_start = datetime.datetime.strptime(value[0], "%d/%m/%Y")
                        date_end = datetime.datetime.strptime(value[1], "%d/%m/%Y")
                        element["type"] = "DATE"
                        element["rangeStart"] = date_start.strftime("%Y%m%d")
                        element["rangeEnd"] = date_end.strftime("%Y%m%d")
                    except ValueError:
                        value = value_temp.split('|')
                        element["value"] = value
                filters_download.append(element)
            filters_download = str(filters_download).replace("'", '"')

        auth_endpoint = _make_url_auth(plataform_url)
        credentials = {"login": str(username), "password": str(password)}
        auth_post = requests.post(auth_endpoint, json=credentials)
        headers = {
            'x-authorization-user-id': auth_post.json()['userId'],
            'x-authorization-token': auth_post.json()['key']
        }
        download_endpoint = _make_download_url(plataform_url)
        payload = {
            'cube': cube,
            'charset': data_format['charset'],
            'delimiter': data_format['delimiter'],
            'quote': data_format['quote'],
            'escape': data_format['escape'],
        }
        if filters:
            payload['filters'] = filters_download
        if columns_download:
            payload['headers'] = columns_download

        with requests.get(download_endpoint, stream=True, headers=headers, params=payload) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    else:
        raise ValueError(ERROR_ARGUMENTS_VALIDATION)

