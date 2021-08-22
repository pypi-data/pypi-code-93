import pydantic


class AnalysisParams(pydantic.BaseModel):
    qasm: pydantic.constr(min_length=1)
