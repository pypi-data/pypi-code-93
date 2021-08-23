from pydantic import BaseModel, Field


class RequestArgs(BaseModel):
    method: str
    path: str
    data: str = ""


class TestMethodArgs(BaseModel):
    name: str = Field(..., description="Name of test method to generate")
    expectation: str = Field(
        ..., description="String representation of pact expectation dictionary"
    )
    request: RequestArgs
