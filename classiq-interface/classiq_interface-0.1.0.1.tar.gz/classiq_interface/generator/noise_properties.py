import pydantic
from typing import Optional, Literal


class NoiseProperties(pydantic.BaseModel):

    # Must be synced with hybrid.hardware_noise_models.hardware_noise_dict
    _HARDWARE_NAMES = (
        "ibmq_16_melbourne",
        "ibmq_armonk",
        "ibmq_athens",
        "ibmq_belem",
        "ibmq_lima",
        "ibmq_quito",
        "ibmq_santiago",
        "ibmqx2",
        "ibmq_manila",
    )

    measurement_bit_flip_probability: Optional[
        pydantic.confloat(ge=0, le=1)
    ] = pydantic.Field(
        default=None,
        description="Probability of measuring the wrong value for each qubit.",
    )
    hardware_noise_name: Optional[Literal[_HARDWARE_NAMES]] = pydantic.Field(
        default=None, description="Name of hardware to simulate its noise"
    )

    @pydantic.validator("hardware_noise_name")
    def validate_hardware_noise_simulator_alone(cls, hardware_noise_name, values):
        if not hardware_noise_name:
            return

        # Hardware noise model cannot work with more noise
        if any(v is not None for v in values.values()):
            raise ValueError(
                "Hardware noise model cannot be changed with additional noise."
            )

        return hardware_noise_name
