import json
import requests

from common.configuration.httpClientConfig import HttClientConfig
from common.dto.logCreateDto import LogCreateDto
from common.dto.logRequestDto import LogRequestDto
from common.enum.logLevel import LogLevel
from common.enum.platform import Platform

with requests.Session() as session:
    session.headers.update({
        'Content-Type': 'application/json',
    })


    def init(api_key):
        response = session.post(f'{HttClientConfig.alertNowURL}/users/sign-in-with-api-key/{api_key}')
        if response.status_code != 200:
            return response

        session.headers.update({
            'Authorization': f'Bearer {response.text}'
        })

        return 'Connection was initialized successfully'


    def info(message):
        return create_log(LogCreateDto(LogLevel.INFO.value, message))


    def error(occurred_error):
        return create_log(LogCreateDto(LogLevel.ERROR.value, json.dumps(vars(occurred_error))))


    def create_log(log_create_dto):
        log_request_dto = LogRequestDto(Platform.PYTHON.value, json.dumps(vars(log_create_dto)))
        response = session.post(f'{HttClientConfig.alertNowURL}/logs/create', data=json.dumps(vars(log_request_dto)))
        return response
