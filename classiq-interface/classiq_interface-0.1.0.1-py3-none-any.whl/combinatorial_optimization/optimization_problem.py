from typing import Dict, Union
import pydantic

from classiq_interface.backend.backend_preferences import (
    IBMBackendPreferences,
    AwsBackendPreferences,
    AzureBackendPreferences,
)
from classiq_interface.hybrid.vqe_problem import VQEPreferences


class OptimizationProblem(pydantic.BaseModel):
    vqe_preferences: VQEPreferences = pydantic.Field(
        default_factory=VQEPreferences, description="preferences for the VQE execution"
    )
    serialized_model: Dict = None
    backend_preferences: Union[
        AzureBackendPreferences, IBMBackendPreferences, AwsBackendPreferences
    ] = pydantic.Field(
        default_factory=lambda: IBMBackendPreferences(
            backend_service_provider="IBMQ", backend_name="aer_simulator"
        ),
        description="Preferences for the requested backend to run the quantum circuit.",
    )
