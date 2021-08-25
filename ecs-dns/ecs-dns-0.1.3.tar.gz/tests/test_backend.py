#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ecs_dns` package."""

import pytest
import os

from pprint import pprint
from pathlib import Path

import boto3
import responses

from moto import mock_ec2

from ecs_dns import find_private_ips, find_public_ips, METADATA_URL
from ecs_dns._ecs_dns import _get_network_info
from tests.mock_data import read_mock_metadata, MOCK_DNI_PRIVATE_IP


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@responses.activate
def test_metadata_parse():
    """Test metadata parsing using mock data."""
    responses.add(
        responses.GET,
        METADATA_URL,
        body=read_mock_metadata(),
        status=200,
    )

    assert list(find_private_ips()) == ["10.0.2.106", "10.0.2.106"]


@mock_ec2
def test_get_network_info(aws_credentials):
    """Test parsing boto3 response."""
    # using a dummy ec2 instance since the describe network interfaces call
    # works the same way with fargate
    client = boto3.client("ec2", region_name="us-east-1")
    vpc_id = client.describe_vpcs()["Vpcs"][0]["VpcId"]
    subnets = client.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
    subnet_id = subnets["Subnets"][0]["SubnetId"]
    client.modify_vpc_attribute(
        EnableDnsSupport={"Value": True},
        VpcId=vpc_id,
    )
    client.modify_vpc_attribute(
        EnableDnsHostnames={"Value": True},
        VpcId=vpc_id,
    )
    resp = client.create_network_interface(
        PrivateIpAddress=MOCK_DNI_PRIVATE_IP, SubnetId=subnet_id
    )
    eni_id = resp["NetworkInterface"]["NetworkInterfaceId"]
    resp = client.describe_network_interfaces(
        Filters=[{"Name": "network-interface-id", "Values": [eni_id]}]
    )
    association = resp["NetworkInterfaces"][0]["Association"]
    expected_ip = association["PublicIp"]
    expected_dns = association["PublicDnsName"]
    found_ip = list(_get_network_info(MOCK_DNI_PRIVATE_IP, "PublicIp"))[0]
    found_dns = list(_get_network_info(MOCK_DNI_PRIVATE_IP, "PublicDnsName"))[0]
    assert expected_ip == found_ip
    assert expected_dns == found_dns
