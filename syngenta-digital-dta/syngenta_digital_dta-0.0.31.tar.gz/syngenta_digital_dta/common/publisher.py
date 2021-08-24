import boto3
import simplejson as json

from syngenta_digital_dta.common import logger


def publish(**kwargs):
    if not kwargs.get('arn') or not kwargs.get('data'):
        return
    try:
        publisher = boto3.client('sns', region_name=kwargs.get('region'))
        publisher.publish(
            TopicArn=kwargs['arn'],
            Message=json.dumps(kwargs['data']),
            MessageAttributes=kwargs.get('attributes', {})
        )
    except Exception as e:
        logger.log(level='WARN', log={'error': 'publish_sns_error: {}'.format(e)})
