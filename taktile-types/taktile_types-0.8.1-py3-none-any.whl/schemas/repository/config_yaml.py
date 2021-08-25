"""Datastructures and validatation for taktile config"""
import typing as t

from pydantic import BaseModel
from pydantic.class_validators import root_validator

from taktile_types.schemas.repository.resources import (
    SIZE_MAP,
    ResourceRequirement,
)


class ServiceWithSizing(BaseModel):
    """Service scaling and sizing information"""

    replicas: int
    requests: ResourceRequirement

    @root_validator(pre=True)
    def service_validator(
        cls, vals
    ):  # pylint: disable=no-self-argument,no-self-use
        """Validates individual service"""
        instance_type_set = "instance_type" in vals
        requests_set = (
            "requests" in vals
            and vals["requests"].cpu is not None
            and vals["requests"].memory is not None
        )
        if instance_type_set and requests_set:
            raise ValueError(
                "Both instance type and requests were found"
                " during validation of service config"
            )
        if not instance_type_set and not requests_set:
            raise ValueError(
                "Neither instance type nor requests were found"
                " during validation of service config"
            )
        if instance_type_set:
            instance_type = vals["instance_type"].split(".")
            if len(instance_type) < 2:
                raise ValueError("Instance type must contain a dot")
            if len(instance_type) > 2:
                raise ValueError(
                    "Instance type cannot contain more than one dot"
                )
            instance_class, instance_size = instance_type
            try:
                vals["requests"] = SIZE_MAP[instance_class][instance_size]
            except KeyError:
                raise ValueError(  # pylint: disable=raise-missing-from
                    "Invalid instance type"
                )
        if vals["replicas"] < 0:
            raise ValueError("Replica count must be non-negative")
        return vals


class RestServiceConfig(BaseModel):
    """Additional info for REST services"""

    max_replicas: int


class TktlServiceConfig(BaseModel):
    """Config info for all services"""

    rest: RestServiceConfig
    arrow: ServiceWithSizing


class TaktileYAMLConfig(BaseModel):
    """data structure for full taktile config yaml"""

    deployment_prefix: t.Optional[str]
    undeployment_prefix: t.Optional[str]
    service: TktlServiceConfig
    version: str
