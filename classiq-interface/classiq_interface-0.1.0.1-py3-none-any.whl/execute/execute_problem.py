from typing import Optional, List, Union

import pydantic

from classiq_interface.generator.generation_metadata import GenerationMetadata
from classiq_interface.backend.backend_preferences import (
    AwsBackendPreferences,
    IBMBackendPreferences,
    AzureBackendPreferences,
)


class AmplitudeEstimation(pydantic.BaseModel):
    alpha: float = pydantic.Field(
        default=0.05, description="Confidence level of the AE algorithm"
    )
    epsilon: float = pydantic.Field(
        default=0.01, description="precision for estimation target `a`"
    )
    binary_search_threshold: Optional[pydantic.confloat(ge=0, le=1)] = pydantic.Field(
        description="The required probability on the tail of the distribution (1 - percentile)"
    )


class AmplitudeAmplification(pydantic.BaseModel):
    iterations: Union[List[int], int, None] = pydantic.Field(
        default=None, description="Number or list of numbers of iteration to use"
    )
    growth_rate: Optional[float] = pydantic.Field(
        default=None,
        description="Number of iteration used is set to round(growth_rate**iterations)",
    )
    sample_from_iterations: bool = pydantic.Field(
        default=False,
        description="If True, number of iterations used is picked randomly from [1, iteration] range",
    )


class GeneralPreferences(pydantic.BaseModel):
    num_shots: int = 100
    amplitude_estimation: Optional[AmplitudeEstimation] = pydantic.Field(
        default_factory=AmplitudeEstimation
    )
    amplitude_amplification: Optional[AmplitudeAmplification] = pydantic.Field(
        default_factory=AmplitudeAmplification
    )
    backend_preferences: Union[
        AzureBackendPreferences, IBMBackendPreferences, AwsBackendPreferences
    ] = pydantic.Field(
        default_factory=lambda: IBMBackendPreferences(
            backend_service_provider="IBMQ", backend_name="aer_simulator_statevector"
        ),
        description="Preferences for the requested backend to run the quantum circuit.",
    )


class ExecuteProblem(pydantic.BaseModel):
    problem_preferences: GeneralPreferences = pydantic.Field(
        default_factory=GeneralPreferences, description="preferences for the execution"
    )

    problem_data: GenerationMetadata = pydantic.Field(
        default=None, description="Data returned from the generation procedure."
    )
