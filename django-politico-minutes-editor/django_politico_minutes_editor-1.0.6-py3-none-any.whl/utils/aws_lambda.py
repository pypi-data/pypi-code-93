import boto3
import json
from django.conf import settings


session = boto3.session.Session(
    region_name='us-east-1',
    aws_access_key_id=settings.MINUTES_AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.MINUTES_AWS_SECRET_ACCESS_KEY
)

aws_lambda = session.client('lambda')


class BakeryResponse:
    ok = None
    status_code = None
    body = None
    headers = None

    def __init__(self, resp):
        resp_payload = resp['Payload']
        resp_body = resp_payload.read()

        parsed_body = json.loads(resp_body)

        self.status_code = parsed_body['statusCode']
        self.body = json.loads(parsed_body["body"])
        self.headers = parsed_body['headers']

        self.ok = self.status_code >= 200 and self.status_code < 300


def invoke(payload, func_name=settings.MINUTES_BAKERY_FUNCTION_NAME):
    resp = aws_lambda.invoke(
        FunctionName=func_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    return BakeryResponse(resp)
