import boto3
from enum import Enum
from phcli.ph_aws.aws_root import PhAWS


class PhMetricDataUnit(Enum):
    SECONDS = 'Seconds'
    MCS = 'Microseconds'
    MS = 'Milliseconds'
    BYTES = 'Bytes'
    KB = 'Kilobytes'
    MB = 'Megabytes'
    GB = 'Gigabytes'
    TB = 'Terabytes'
    BITS = 'Bits'
    KBI = 'Kilobits'
    MBI = 'Megabits'
    GBI = 'Gigabits'
    TBI = 'Terabits'
    PERCENT = 'Percent'
    COUNT = "Count"
    BYTES_SECOND = "Bytes/Second"
    KB_SECOND = "Kilobytes/Second"
    MB_SECOND = "Megabytes/Second"
    GB_SECOND = "Gigabytes/Second"
    TB_SECOND = "Terabytes/Second"
    BITS_SECOND = "Bits/Second"
    KBI_SECOND = "Kilobits/Second"
    MBI_SECOND = "Megabits/Second"
    GBI_SECOND = "Gigabits/Second"
    TBI_SECOND = "Terabits/Second"
    COUNT_SECOND = "Count/Second"
    NONE = "None"


class PhMetricData(object):
    def __init__(self, metric_name, dimensions, value, unit: PhMetricDataUnit, storage_resolution=60):
        self.metric_name = metric_name
        self.dimensions = [{"Name": k, "Value": v} for k,v in dimensions.items()]
        self.value = value
        self.unit = unit
        self.storage_resolution = storage_resolution

    def to_dict(self):
        return {
            'MetricName': self.metric_name,
            'Dimensions': self.dimensions,
            'Value': self.value,
            'Unit': self.unit.value,
            'StorageResolution': self.storage_resolution,
        }


class PhCloudWatch(PhAWS):
    def __init__(self, *args, **kwargs):
        self.access_key = kwargs.get('access_key', None)
        self.secret_key = kwargs.get('secret_key', None)
        if self.access_key and self.secret_key:
            self.cw_client = boto3.client('cloudwatch', region_name='cn-northwest-1',
                                          aws_access_key_id=self.access_key,
                                          aws_secret_access_key=self.secret_key)
            self.cw_resource = boto3.resource('cloudwatch', region_name='cn-northwest-1',
                                              aws_access_key_id=self.access_key,
                                              aws_secret_access_key=self.secret_key)
            return

        self.phsts = kwargs.get('phsts', None)
        if self.phsts and self.phsts.credentials:
            self.cw_client = boto3.client('cloudwatch', **self.phsts.get_cred())
            self.cw_resource = boto3.resource('cloudwatch', **self.phsts.get_cred())
            return

        self.cw_client = boto3.client('cloudwatch')
        self.cw_resource = boto3.resource('cloudwatch')

    def put_metric_data(self, namespace, *metricdatas):
        return self.cw_client.put_metric_data(
            Namespace=namespace,
            MetricData=[md.to_dict() for md in metricdatas]
        )


if __name__ == '__main__':
    import base64
    from phcli.ph_aws.ph_sts import PhSts
    from phcli import define_value as dv

    phsts = PhSts().assume_role(
        base64.b64decode(dv.ASSUME_ROLE_ARN).decode(),
        dv.ASSUME_ROLE_EXTERNAL_ID,
    )
    phcw = PhCloudWatch(phsts=phsts)

    response = phcw.put_metric_data("PhApp", PhMetricData("Call", {"User": "alfred", "Type": "cli", "API": "maxauto.delete"}, 1, PhMetricDataUnit.COUNT))
    print(response)
    print(type(response))



