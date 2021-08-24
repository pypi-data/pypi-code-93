#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille <john@ews-network.net>

"""Definition of Custom::KafkaTopic."""

from troposphere.cloudformation import CustomResource
from troposphere.validators import positive_integer

from aws_custom_ews_kafka_resources import KafkaAclPolicy


class KafkaTopic(CustomResource):
    """
    Class to represent EWS::Kafka::Topic
    """

    resource_type = "Custom::KafkaTopic"

    props = {
        "BootstrapServers": (str, True),
        "ReplicationFactor": (positive_integer, False),
        "SecurityProtocol": (str, False),
        "SASLMechanism": (str, False),
        "SASLUsername": (str, False),
        "SASLPassword": (str, False),
        "Name": (str, True),
        "PartitionsCount": (positive_integer, True),
        "Settings": (dict, False),
        "ServiceToken": (str, True),
    }


class KafkaAcl(CustomResource):
    """
    Class to represent Custom::KafkaACL
    """

    resource_type = "Custom::KafkaACL"

    props = {
        "BootstrapServers": (str, True),
        "ReplicationFactor": (positive_integer, False),
        "SecurityProtocol": (str, False),
        "SASLMechanism": (str, False),
        "SASLUsername": (str, False),
        "SASLPassword": (str, False),
        "ServiceToken": (str, True),
        "Policies": ([KafkaAclPolicy], True),
    }


class KafkaTopicSchema(CustomResource):
    """
    Class to represent Custom::KafkaSchema
    """

    resource_type = "Custom::KafkaSchema"

    props = {
        "RegistryUrl": (str, True),
        "RegistryUsername": (str, False),
        "RegistryPassword": (str, False),
        "Subject": (str, True),
        "Type": (str, True),
        "Definition": ((str, dict), True),
        "SerializeAttribute": (str, True),
        "CompatibilityMode": (str, True),
        "ServiceToken": (str, True),
    }
