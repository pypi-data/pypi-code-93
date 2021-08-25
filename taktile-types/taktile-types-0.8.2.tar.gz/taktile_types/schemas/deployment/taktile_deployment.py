"""Deployment related datastructures"""
import typing as t

from pydantic import BaseModel

from taktile_types.enums.instance import InstanceSize, InstanceType


class DeploymentMetadata(BaseModel):
    """
    Metadata of the deployment

    Attributes
    ----------

    name: str
        name used by kubernetes
    """

    name: str


class DeploymentSpec(BaseModel):
    """
    Full specification of the deployment

    Attributes
    ----------

    ref: str
        Branch or tag
    commit: str
        Full commit hash
    repository_uri: str
        URI of repository on github
    principal: str
        user or organization which own the repo
    rest_instance_size: Optional[InstanceSize]
        enumeration of size
    rest_instance_type: Optional[InstanceType]
        enumeration of type
    rest_cpu_request: Optional[str]
        kubernetes-parsable cpu request
    rest_memory_request: Optiona[str]
        kubernetes-parsable memory request
    arrow_instance_size: Optional[InstanceSize]
        enumeration of size
    arrow_instance_type: Optional[InstanceType]
        enumeration of type
    arrow_cpu_request: Optional[str]
        kubernetes-parsable cpu request
    arrow_memory_request: Optiona[str]
        kubernetes-parsable memory request
    rest_replicas: int
        min count for rest replicas
    max_rest_replicas: int
        max scale for rest replicas
    arrow_replicas: int
        static scale for arrow replicas

    repository_key: str
    repository_id: str
        uuid for associated repository

    github_auth_volume: str
        name of volume containing github token
    taktile_auth_volume: str
        name of volume containing taktile token
    api_key_auth_volume: str
        name of volume containing api key
    repository_secret_auth_volume: str
        name of volume containing repo secrets


    """

    ref: str
    commit: str
    repository_uri: str

    principal: str

    rest_instance_size: t.Optional[InstanceSize]
    rest_instance_type: t.Optional[InstanceType]
    rest_cpu_request: t.Optional[str]
    rest_memory_request: t.Optional[str]
    rest_gpu_request: t.Optional[str]

    arrow_instance_size: t.Optional[InstanceSize]
    arrow_instance_type: t.Optional[InstanceType]
    arrow_cpu_request: t.Optional[str]
    arrow_memory_request: t.Optional[str]
    arrow_gpu_request: t.Optional[str]

    rest_replicas: int
    max_rest_replicas: int
    arrow_replicas: int

    repository_key: str
    repository_id: str

    github_auth_volume: str
    taktile_auth_volume: str
    api_key_auth_volume: str
    repository_secret_auth_volume: str


class Deployment(BaseModel):
    """
    Top-level TD Object

    Attributes
    ----------

    apiVersion: str
        version of the CRD to use
    kind: str
        identifier for CRD type
    spec: DeploymentSpec
        full spec for TD
    metadata: DeploymentSpec
        object meta including name
    """

    apiVersion: str
    kind: str
    spec: DeploymentSpec
    metadata: DeploymentMetadata


class SecretMetadata(BaseModel):
    """
    Secret object metadata

    Attributes
    ----------
    name: str
        name of object
    """

    name: str


class RepositorySecret(BaseModel):
    """
    Secret contents

    Attributes
    ----------
    secret_name: str
        name of individual secret
    secret_value: str
        content of individual secret

    """

    secret_name: str
    secret_value: str


class Secret(BaseModel):
    """
    Top-level secret object

    Attributes
    ----------
    token: str
        secret token
    metadata: SecretMetadata
        identifier for object
    """

    token: str
    metadata: SecretMetadata


class ApplyPayload(BaseModel):
    """
    Fully serialization of deployment payload

    Attributes
    ----------
    secret: Secret
        secret used in update
    deployment: Deployment
        Full TD object
    repository_secret: List[RepositorySecret]
        list of all repo secrets
    update_key: str
        key to write back to taktile APIs
    api_key: str
        key to authenticate against model
    """

    secret: Secret
    deployment: Deployment
    repository_secrets: t.List[RepositorySecret]
    update_key: str
    api_key: str
