from pathlib import Path
import datetime
from dateutil.tz import tzutc


def read_mock_metadata() -> str:
    path = Path(__file__).resolve().parent / "mock_metadata.json"
    with open(path, "r") as fh:
        return fh.read()


MOCK_DNI_PRIVATE_IP = "172.31.10.10"
MOCK_DNI_PUBLIC_IP = "50.200.80.30"
MOCK_DNI_PUBLIC_DNS = "ec2-50-200-80-30.compute-1.amazonaws.com"
MOCK_DNI_RESPONSE = {
    "NetworkInterfaces": [
        {
            "Association": {
                "IpOwnerId": "amazon",
                "PublicDnsName": MOCK_DNI_PUBLIC_DNS,
                "PublicIp": MOCK_DNI_PUBLIC_IP,
            },
            "Attachment": {
                "AttachTime": datetime.datetime(2021, 8, 1, 1, 1, 1, tzinfo=tzutc()),
                "AttachmentId": "eni-attach-123456789abcdefgh",
                "DeleteOnTermination": False,
                "DeviceIndex": 1,
                "NetworkCardIndex": 0,
                "InstanceOwnerId": "111111111111",
                "Status": "attached",
            },
            "AvailabilityZone": "us-east-1c",
            "Description": "arn:aws:ecs:us-east-1:111111111111:attachment/11111111-1234-1234-1234-111111111111",
            "Groups": [
                {"GroupName": "fake-security-group", "GroupId": "sg-123456789abcdefgh"}
            ],
            "InterfaceType": "interface",
            "Ipv6Addresses": [],
            "MacAddress": "12:34:56:78:90:12",
            "NetworkInterfaceId": "eni-123456789abcdefgh",
            "OwnerId": "111111111111",
            "PrivateDnsName": f"ip-{MOCK_DNI_PRIVATE_IP.replace('.', '-')}.ec2.internal",
            "PrivateIpAddress": MOCK_DNI_PRIVATE_IP,
            "PrivateIpAddresses": [
                {
                    "Association": {
                        "IpOwnerId": "amazon",
                        "PublicDnsName": MOCK_DNI_PUBLIC_DNS,
                        "PublicIp": MOCK_DNI_PUBLIC_IP,
                    },
                    "Primary": True,
                    "PrivateDnsName": f"ip-{MOCK_DNI_PRIVATE_IP.replace('.', '-')}.ec2.internal",
                    "PrivateIpAddress": MOCK_DNI_PRIVATE_IP,
                }
            ],
            "RequesterId": "123456789123",
            "RequesterManaged": True,
            "SourceDestCheck": True,
            "Status": "in-use",
            "SubnetId": "subnet-11111111",
            "TagSet": [
                {"Key": "aws:ecs:clusterName", "Value": "my-cluster"},
                {"Key": "aws:ecs:serviceName", "Value": "my-service"},
            ],
            "VpcId": "vpc-11111111",
        }
    ],
    "ResponseMetadata": {
        "RequestId": "6a870193-45a3-4a6b-a892-a1ec5caa6031",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "x-amzn-requestid": "6a870193-45a3-4a6b-a892-a1ec5caa6031",
            "cache-control": "no-cache, no-store",
            "strict-transport-security": "max-age=31536000; includeSubDomains",
            "content-type": "text/xml;charset=UTF-8",
            "content-length": "3112",
            "vary": "accept-encoding",
            "date": "Tue, 24 Aug 2021 20:35:22 GMT",
            "server": "AmazonEC2",
        },
        "RetryAttempts": 0,
    },
}
