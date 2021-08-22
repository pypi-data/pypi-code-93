import pydantic
from classiq_interface.generator.circuit_outline import Qubit
from classiq_interface.generator.slides import Slide, PhaseSlide


class CXSlideEntangler(Slide):
    """
    A slide of CX gates
    """

    # TODO: Replace to valid qubit.
    slide_first_control: Qubit = pydantic.Field(
        default=..., description="The control qubit of the first CX gate in the slide"
    )

    @pydantic.validator("slide_first_control")
    def first_control_validator(cls, first_control, values):
        targets = values.get("slide_targets")

        if targets is not None and first_control in targets:
            # TODO: Find out whether it is true.
            raise ValueError("first control can not be a target in the slide")

        return first_control


class PhaseCXSlideEntangler(PhaseSlide, CXSlideEntangler):
    pass


class SquareClusterEntanglerParameters(pydantic.BaseModel):
    num_of_qubits: pydantic.conint(ge=2)
    schmidt_rank: pydantic.conint(ge=0)


class Open2DClusterEntanglerParameters(pydantic.BaseModel):
    qubit_count: pydantic.conint(ge=2)
    schmidt_rank: pydantic.conint(ge=0)
