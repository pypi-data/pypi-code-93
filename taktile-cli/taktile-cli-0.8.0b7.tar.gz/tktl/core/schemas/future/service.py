import typing as t

from pydantic import BaseModel

from tktl.core.future.t import ArrowFormatKinds, EndpointKinds, ProfileKinds


class EndpointInfoSchema(BaseModel):
    name: str
    path: str
    kind: EndpointKinds
    profile_kind: t.Optional[ProfileKinds]
    explain_path: t.Optional[str]
    response_kind: t.Optional[ArrowFormatKinds]
    input_names: t.List[str] = []
    output_names: t.Optional[str] = None
    profile_columns: t.Optional[t.List[str]] = None
    input_example: t.Optional[t.List[t.Any]] = None
    output_example: t.Optional[t.List[t.Any]] = None
    explainer_example: t.Optional[t.List[t.Any]] = None


class InfoEndpointResponseModel(BaseModel):
    schema_version: str
    taktile_cli: str
    profiling: str
    endpoints: t.List[EndpointInfoSchema]
