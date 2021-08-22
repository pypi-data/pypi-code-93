import pydantic


class PhaseEstimation(pydantic.BaseModel):
    phase_estimation_phase: pydantic.confloat(ge=0)
