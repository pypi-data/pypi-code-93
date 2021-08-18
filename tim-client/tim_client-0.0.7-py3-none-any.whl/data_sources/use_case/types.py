from typing_extensions import TypedDict


class UseCaseConfiguration(TypedDict):
  name: str
  workspaceId: str
  datasetId: str


class CreateUseCaseResponse(TypedDict):
  id: str
  name: str
  description: str
  input: str
  output: str
  businessValue: str
  businessObjective: str
  businessKpi: str
  accuracyImpact: int
  workspaceId: str
  datasetId: str
  isFavorite: bool
  createdAt: str
  createdBy: str
