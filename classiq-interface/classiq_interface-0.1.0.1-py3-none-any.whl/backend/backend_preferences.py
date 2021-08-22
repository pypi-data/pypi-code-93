from typing import Literal, Optional
import pydantic

from classiq_interface.backend.quantum_backend_providers import (
    ProviderVendor,
    BACKEND_PROVIDERS_DICT,
)


class BackendPreferences(pydantic.BaseModel):
    backend_service_provider: str = pydantic.Field(
        description="Provider company for the requested backend."
    )
    backend_name: str = pydantic.Field(description="Name of the requested backend.")


class AwsBackendPreferences(BackendPreferences):
    _BACKEND_SERVICE_PROVIDER = ProviderVendor.AWS_BRAKET
    backend_service_provider: Literal[_BACKEND_SERVICE_PROVIDER.value]
    backend_name: Literal[
        tuple(name.value for name in BACKEND_PROVIDERS_DICT[_BACKEND_SERVICE_PROVIDER])
    ]
    aws_access_key_id: Optional[str] = pydantic.Field(description="AWS Access Key ID")
    aws_secret_access_key: Optional[str] = pydantic.Field(
        description="AWS Secret Access Key"
    )
    region_name: Optional[str] = pydantic.Field(description="AWS Region name")
    s3_bucket_name: str = pydantic.Field(description="S3 Bucket Name")
    s3_bucket_key: str = pydantic.Field(description="S3 Bucket Key")


class IBMBackendPreferences(BackendPreferences):
    _BACKEND_SERVICE_PROVIDER = ProviderVendor.IBMQ
    backend_service_provider: Literal[_BACKEND_SERVICE_PROVIDER.value]
    backend_name: Literal[
        tuple(name.value for name in BACKEND_PROVIDERS_DICT[_BACKEND_SERVICE_PROVIDER])
    ]


class AzureBackendPreferences(BackendPreferences):
    _BACKEND_SERVICE_PROVIDER = ProviderVendor.AZURE_QUANTUM
    backend_service_provider: Literal[_BACKEND_SERVICE_PROVIDER.value]
    backend_name: Literal[
        tuple(name.value for name in BACKEND_PROVIDERS_DICT[_BACKEND_SERVICE_PROVIDER])
    ]
