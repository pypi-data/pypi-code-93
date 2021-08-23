"""Execute AWS operations."""
from typing import Union


__version__ = '2021.1.0.0'


class WriteLog(object):
    """
    Create JSON log object for CloudWatch.

    # Import modules.
    import json
    from aws_snippets import WriteLog

    # Initiate with empty dictionary.
    logger = WriteLog({})

    # Collect entries to log.
    logger.log('<strkey>', '<value>')
    logger.log('<intkey>', <value>)
    logger.log('<boolkey>', <True/False>)

    # Print out to CloudWatch as accumulated log.
    print(json.dumps(logger.text))
    """

    def __init__(self, text):
        """Initialize log content."""
        self.text = text

    def log(self, key, value):
        """Update log content."""
        self.text[key] = value


def cleantmp(
    tmppath: str
) -> None:
    """
    Clean Lambda /tmp path.

    return None
    """
    import os
    import shutil

    if os.path.exists(tmppath):
        shutil.rmtree(tmppath)
    for filename in os.listdir('/tmp'):
        file_path = os.path.join('/tmp', filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    return None


def readsecret(
    id: str
) -> str:
    """Read secret values in AWS Secrets Manager.

    return str
    """
    import boto3
    from botocore.exceptions import ClientError

    secrets = boto3.client('secretsmanager')
    response = secrets.get_secret_value(SecretId=id)

    return response


def b64encode(
    cleartext: str,
    encoding: str = 'latin-1'
) -> str:
    """
    Encode strings using Base64.

    return str
    """
    import base64

    clearbyte = cleartext.encode(encoding)
    cipherbyte = base64.urlsafe_b64encode(clearbyte)
    ciphertext = cipherbyte.decode(encoding)

    return ciphertext


def kmsencrypt(
    cleartext: str,
    kmsid: str
) -> str:
    """Encrypt strings using AWS KMS.

    return str
    """
    import boto3

    kms = boto3.client('kms')
    response = kms.encrypt(
        KeyId=kmsid,
        Plaintext=cleartext
    )

    return response['CiphertextBlob']


def kmsdecrypt(
    ciphertext: str,
    kmsid: str
) -> str:
    """Decrypt strings using AWS KMS.

    return str
    """
    import boto3

    kms = boto3.client('kms')
    response = kms.decrypt(
        KeyId=kmsid,
        CiphertextBlob=ciphertext
    )

    return response['Plaintext']


def sha3512hash(
    clrtxt: str,
    condiments: str,
    encoding: str = 'latin-1'
) -> str:
    """
    Hash strings using SHA3_512 algorithm.

    return str
    """
    import hashlib

    clrslt = '{}{}'.format(clrtxt, condiments)
    clrbyte = clrslt.encode(encoding)
    hashbyte = hashlib.sha3_512(clrbyte)
    hashstr = hashbyte.hexdigest()

    return hashstr


def httppost(
    url: str,
    headers: dict = dict(),
    data: dict = dict(),
    encoding: str = 'latin-1'
) -> str:
    """
    Make HTTP requests using POST method.

    return str
    """
    import json
    from urllib import request, error, parse

    databyte = json.dumps(data).encode(encoding)
    req = request.Request(
        url,
        headers=headers,
        data=databyte,
        method='POST'
    )
    with request.urlopen(req) as response:
        read_response = response.read().decode(encoding)

    return read_response


def httpget(
    url: str,
    headers: dict = dict(),
    encoding: str = 'latin-1'
) -> dict:
    """
    Make HTTP requests using GET method.

    return dict
    """
    import json
    from urllib import request, error, parse

    req = request.Request(
        url,
        headers=headers,
        method='GET'
    )
    with request.urlopen(req) as response:
        read_response = response.read().decode(encoding)

    return read_response


def cfpurge(
    cf_dist: str,
    path: str,
    call_ref: str
) -> dict:
    """
    Create Amazon CloudFront cache invalidation.

    return dict
    """
    import boto3

    cloudfront = boto3.client('cloudfront')
    response = cloudfront.create_invalidation(
        DistributionId=cf_dist,
        InvalidationBatch={
            'Paths': {
                'Quantity': 1,
                'Items': [
                    path
                ]
            },
            'CallerReference': call_ref
        }
    )

    return response


def randomize(
    length: int,
    punctuations: bool = False
) -> str:
    """
    Create random strings.

    return str
    """
    import random
    import string

    if punctuations is True:
        response = ''.join(
            random.choices(
                string.ascii_lowercase +
                string.ascii_uppercase +
                string.digits +
                string.punctuation,
                k=length
            )
        )
    else:
        response = ''.join(
            random.choices(
                string.ascii_lowercase +
                string.ascii_uppercase +
                string.digits,
                k=length
            )
        )

    return response


def snsnotify(
    topic: str,
    message: str,
    subject: str
) -> None:
    """
    Send AWS SNS notifications.

    return None
    """
    import boto3

    sns = boto3.client('sns')
    responsesns = sns.publish(
        TopicArn=topic,
        Message=message,
        Subject=subject
    )

    return None


def sqsmessage(
    queue_url: str,
    message: dict
) -> dict:
    """
    Send messages into AWS SQS queues.

    return dict
    """
    import json
    import boto3

    sqs = boto3.client('sqs')
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    )

    return response


def sanitizervalidate(
    input: str,
    pattern: str
) -> bool:
    """
    Validate input items to RegEx patterns.

    return bool
    """
    import re

    try:

        assert input
        assert len(input) > 0
        assert str(input).strip() != ''
        assert re.search(pattern, str(input))

        return True

    except Exception as e:

        return False


def sanitizerclean(
    input: str
) -> str:
    """
    Sanitize input items.

    return str
    """
    import re

    new_input = str(input).replace(';', '').replace('|', '').strip()

    return new_input


def sanitizercleanurl(
    url: str
) -> str:
    """
    Sanitize input URLs.

    return str
    """
    import re

    new_url = str(url).replace(';', '%3B').replace('|', '%7C').strip()

    return new_url


def sanitizervalidatelist(
    input: list
) -> bool:
    """
    Validate input list.

    return bool
    """
    import re

    try:

        assert input
        assert len(input) > 0
        assert set(input) != {''}
        assert isinstance(input, list)

        return True

    except Exception as e:

        return False


def sanitizercleanlist(
    input: list,
    pattern: str
) -> list:
    """
    Sanitize input list.

    return list
    """
    import re

    new_list = list()
    for item in input:
        if sanitizervalidate(item, pattern):
            new_item = sanitizerclean(item)
            new_list.append(new_item)

    return new_list


def sanitizercleanurllist(
    input: list,
    pattern: str
) -> list:
    """
    Sanitize input list.

    return list
    """
    import re

    new_list = list()
    for item in input:
        if sanitizervalidate(item, pattern):
            new_item = sanitizercleanurl(item)
            new_list.append(new_item)

    return new_list


def dynamodbgetitem(
    table: str,
    key: str,
    value: str
) -> dict:
    """
    Get a single item from DynamoDB.

    return dict
    """
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError

    dynamodb = boto3.resource('dynamodb')
    response = dynamodb.Table(table).get_item(
        Key={
            key: value
        }
    )

    return response['Item']


def dynamodbqueryitems(
    table: str,
    key: str,
    value: str
) -> dict:
    """
    Get items based on keyword query from DynamoDB.

    return dict
    """
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError

    dynamodb = boto3.resource('dynamodb')
    response = dynamodb.Table(table).query(
        KeyConditionExpression=Key(key).eq(value)
    )

    return response['Items']


def dynamodbscanitems(
    table: str,
    key: str,
    value: str,
    patternexp: dict
) -> dict:
    """
    Get all items from a DynamoDB table then filter by expression.

    return dict
    """
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError

    dynamodb = boto3.resource('dynamodb')
    fe = Key(key).eq(value)
    pe = patternexp
    response = dynamodb.Table(table).scan(
        FilterExpression=fe,
        ProjectionExpression=pe
    )

    return response['Items']


def dynamodbscanallitems(
    table: str
) -> dict:
    """
    Get all items from a table in DynamoDB.

    return dict
    """
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError

    dynamodb = boto3.resource('dynamodb')
    response = dynamodb.Table(table).scan()

    return response['Items']


def dynamodbputitem(
    table: str,
    itemdict: dict
) -> None:
    """
    Put a single item into DynamoDB.

    return None
    """
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError

    dynamodb = boto3.resource('dynamodb')
    response = dynamodb.Table(table).put_item(
        Item=itemdict
    )

    return None


def dynamodbdeleteallitems(
    table: str
) -> None:
    """
    Delete all items from a DynamoDB table.

    return None
    """
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError

    dynamodb = boto3.resource('dynamodb')
    response = dynamodb.Table(table).scan()
    with dynamodb.Table(table).batch_writer() as batch:
        for each in response['Items']:
            batch.delete_item(Key=each)

    return None


def dynamodbdeletetable(
    table: str
) -> None:
    """
    Delete a table from DynamoDB.

    return None
    """
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError

    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.describe_table(TableName=table)
        response = dynamodb.delete_table(TableName=table)
        waiter = dynamodb.get_waiter('table_not_exists')
        waiter.wait(
            TableName=table,
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': 10
            }
        )
    except Exception as e:
        pass

    return None


def dynamodbcreatetable(
    table: str,
    attrdictls: list,
    schemadictls: list,
    kmsid: str,
    tagdictls: list
) -> None:
    """
    Create a table in DynamoDB.

    return None
    """
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError

    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.describe_table(TableName=table)
    except Exception as e:
        response = dynamodb.create_table(
            TableName=table,
            AttributeDefinitions=attrdictls,
            KeySchema=schemadictls,
            # BillingMode='PROVISIONED',
            # ProvisionedThroughput={
            #     'ReadCapacityUnits': 25,
            #     'WriteCapacityUnits': 25
            # },
            BillingMode='PAY_PER_REQUEST',
            SSESpecification={
                'Enabled': True,
                'SSEType': 'KMS',
                'KMSMasterKeyId': kmsid
            },
            Tags=tagdictls
        )
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(
            TableName=table,
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': 10
            }
        )

    return None


def dynamodbupdateitem(
    table: str,
    keydict: dict,
    attributedict: dict,
    valuedict: dict,
    updateexpression: str
) -> dict:
    """
    Update an item in a DynamoDB table.

    return dict
    """
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError

    dynamodb = boto3.client('dynamodb')
    response = dynamodb.update_item(
        TableName=table,
        Key=keydict,
        ExpressionAttributeNames=attributedict,
        ExpressionAttributeValues=valuedict,
        UpdateExpression=updateexpression
    )

    return response
