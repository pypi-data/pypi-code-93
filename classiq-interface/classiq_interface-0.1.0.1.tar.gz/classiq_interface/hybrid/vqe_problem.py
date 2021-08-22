import enum
from typing import Optional, List, Union

import pydantic
import qiskit

from classiq_interface.generator.generation_metadata import GenerationMetadata
from classiq_interface.generator.noise_properties import NoiseProperties
from classiq_interface.backend.backend_preferences import (
    AwsBackendPreferences,
    IBMBackendPreferences,
    AzureBackendPreferences,
)


class VerbosityLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"


ANSATZ_EXTENSION = ".qasm"
COST_DATA_EXTENSION = ".json"


class CostType(str, enum.Enum):
    MIN = "MIN"
    AVERAGE = "AVERAGE"
    CVAR = "CVAR"


class VQEPreferences(pydantic.BaseModel):
    qaoa_reps: pydantic.PositiveInt = pydantic.Field(
        default=1, description="Number of layers in qaoa ansatz."
    )
    num_shots: pydantic.PositiveInt = pydantic.Field(
        default=100, description="Number of repetitions of the quantum ansatz."
    )
    cost_type: CostType = pydantic.Field(
        default=CostType.CVAR,
        description="Summarizing method of the measured bit strings",
    )
    external_cost_server: Optional[pydantic.AnyHttpUrl] = pydantic.Field(
        default=None,
        description="URL for external cost server. Format: http://<host>:<port>/score "
        "The server must accept POST requests with field 'trk_list' and return"
        "a response with field 'score'.",
    )
    alpha_cvar: pydantic.confloat(gt=0, le=1) = pydantic.Field(
        default=None, description="Parameter for the CVAR summarizing method"
    )
    max_iteration: pydantic.PositiveInt = pydantic.Field(
        default=100, description="Maximal number of optimizer iterations"
    )
    tolerance: pydantic.PositiveFloat = pydantic.Field(
        default=None, description="Final accuracy in the optimization"
    )
    verbosity_level: VerbosityLevel = pydantic.Field(
        default=VerbosityLevel.DEBUG,
        description="Level of elaboration of the presented output. "
        "INFO stands for critical data only. "
        "DEBUG stands for extended data about the performance.",
    )
    num_presented_solutions: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=3,
        description="Number of presented "
        "solutions. Set to null to "
        "fetch all solutions.",
    )
    use_gpu: bool = pydantic.Field(
        default=True, description="Try simulating on GPU if available."
    )
    invalid_space_cost_threshold: Optional[pydantic.PositiveFloat] = pydantic.Field(
        default=None,
        description="Solutions with cost greater or equal to that value, are considered invalid.",
    )
    is_penalty: bool = pydantic.Field(
        default=True,
        description="Indicates whether to use QAOA with penalty terms or constrained QAOA.",
    )

    @pydantic.validator("alpha_cvar", pre=True, always=True)
    def check_alpha_cvar(cls, alpha_cvar, values):
        if alpha_cvar is not None and values["cost_type"] != CostType.CVAR:
            raise ValueError("Use CVAR params only when relevant.")

        if alpha_cvar is None and values["cost_type"] == CostType.CVAR:
            alpha_cvar = 0.04

        return alpha_cvar


class VQEProblem(pydantic.BaseModel):
    # TODO: add random seed
    vqe_preferences: VQEPreferences = pydantic.Field(
        default_factory=VQEPreferences, description="preferences for the VQE execution"
    )
    ansatz: str = pydantic.Field(
        default=None, description="Qasm containing the ansatz circuit"
    )
    cost_data: GenerationMetadata = pydantic.Field(
        default=None, description="Data returned from the generation procedure."
    )
    is_generate_strings_uniformly: bool = pydantic.Field(
        default=True,
        description="Change the parameter sampling distribution in order to get uniform "
        "distribution on the valid bit strings.",
    )
    warm_start: Optional[List[float]] = pydantic.Field(
        default=None,
        description="Supply a vector of parameter assignments "
        "as an initial guess for the VQE search",
    )
    noise_properties: Optional[NoiseProperties] = pydantic.Field(
        default=None, description="Properties of the noise in the circuit"
    )
    use_mps_simulator: bool = pydantic.Field(
        default=False,
        description="Whether to use a matrix_product_state instead"
        "of statevector simulator. Use to improve"
        "performance of lightly entangled circuits.",
    )
    backend_preferences: Union[
        AzureBackendPreferences, IBMBackendPreferences, AwsBackendPreferences
    ] = pydantic.Field(
        default_factory=lambda: IBMBackendPreferences(
            backend_service_provider="IBMQ", backend_name="aer_simulator"
        ),
        description="Preferences for the requested backend to run the quantum circuit.",
    )

    @pydantic.validator("warm_start")
    def check_num_of_params_assign(cls, warm_start, values):
        if warm_start is None:
            return warm_start

        ansatz = values.get("ansatz")
        circuit_param = qiskit.QuantumCircuit.from_qasm_str(ansatz).parameters

        if len(warm_start) != len(circuit_param):
            raise ValueError(
                "Number of parameters assigned does not match number of parameters in circuit"
            )

        return warm_start
