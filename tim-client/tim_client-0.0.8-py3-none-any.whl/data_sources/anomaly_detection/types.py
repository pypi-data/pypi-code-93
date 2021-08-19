from enum import Enum
from tim.types import Logs
from typing import List, NamedTuple, Optional
from typing_extensions import TypedDict
from pandas.core.frame import DataFrame

Range = TypedDict('Range', {'from': str, 'to': str})


class ImputationTypeEnum(Enum):
  LINEAR = 'Linear'
  LOCF = 'LOCF'
  NONE = 'None'


class BasicBaseUnitEnum(Enum):
  DAY = 'Day'
  HOUR = 'Hour'
  MINUTE = 'Minute'
  SECOND = 'Second'


class ImputationInput(TypedDict):
  type: ImputationTypeEnum
  maxGapLength: int


class TimeScaleInput(TypedDict):
  baseUnit: BasicBaseUnitEnum
  value: int


class UpdateTimeInput(TypedDict):
  type: str
  value: str


class UpdateUntilInput(TypedDict):
  baseUnit: str
  offset: int


class UpdatesInput(TypedDict):
  column: str
  updateTime: List[UpdateTimeInput]
  updateUntil: UpdateUntilInput


class Data(TypedDict):
  versionId: str
  rows: List[Range]
  columns: List[str]
  KPIColumn: str
  holidayColumn: str
  imputation: ImputationInput
  timeScale: TimeScaleInput
  aggregation: str
  updates: List[UpdatesInput]


class DomainSpecificsInput(TypedDict):
  perspective: str
  sensitivity: float
  minSensitivity: float
  maxSensitivity: float


class NormalBehaviorModelInput(TypedDict):
  useNormalBehaviorModel: bool
  normalization: bool
  maxModelComplexity: int
  features: List[str]
  dailyCycle: bool
  useKPIoffsets: bool
  allowOffsets: bool


class DetectionIntervalsInput:
  type: str
  value: str


class AnomalousBehaviorModelInput(TypedDict):
  maxModelComplexity: int
  detectionIntervals: List[DetectionIntervalsInput]


class Configuration(TypedDict):
  domainSpecifics: List[DomainSpecificsInput]
  normalBehaviorModel: NormalBehaviorModelInput
  anomalousBehaviorModel: AnomalousBehaviorModelInput


class AnomalyDetectionJobConfiguration(TypedDict):
  name: str
  useCaseId: str
  data: Data
  configuration: Configuration


class BuildModelResponse(TypedDict):
  id: str
  expectedResultsTableSize: float


class CreateAnomalyDetectionConfiguration(TypedDict):
  name: str
  configuration: Configuration
  data: Data


class ExecuteResponse(TypedDict):
  message: str
  code: str


class AccuracyMetrics(TypedDict):
  mape: float
  rmse: float
  accuracy: str
  mae: float


class SampleMeasures(TypedDict):
  name: str
  inSample: AccuracyMetrics
  outOfSample: AccuracyMetrics


class ErrorMeasures(TypedDict):
  all: SampleMeasures
  bin: List[SampleMeasures]
  samplesAhead: List[SampleMeasures]


class AnomalyDetection(TypedDict):
  id: str
  name: str
  type: str
  status: str
  parentId: str
  sequenceId: str
  useCaseId: str
  experimentId: str
  dataVersionId: str
  createdAt: str
  completedAt: str
  executedAt: str
  workerVersion: float
  registrationBody: AnomalyDetectionJobConfiguration


class Part(TypedDict):
  type: str
  predictor: str
  offset: int
  value: float
  window: int
  knot: float
  subtype: int
  period: int
  cosOrders: List[float]
  sinOrder: List[float]
  unit: str
  day: int
  month: int


class Term(TypedDict):
  importance: int
  parts: List[Part]


class VariableOffset(TypedDict):
  name: str
  dataFrom: int
  dataTo: int


class AnomalyDetectionJobNormalBehaviorModelModel(TypedDict):
  index: int
  dayTime: str
  terms: List[Term]
  variableOffsets: List[VariableOffset]


class VariableProperties(TypedDict):
  name: str
  importance: float


class AnomalyDetectionJobNormalBehaviorModel(TypedDict):
  samplingPeriod: str
  models: List[AnomalyDetectionJobNormalBehaviorModelModel]
  variableProperties: List[VariableProperties]


class AnomalyDetectionJobModelResultModel(TypedDict):
  normalBehaviorModel: AnomalyDetectionJobNormalBehaviorModel


class AnomalyDetectionJobModelResult(TypedDict):
  modelVersion: str
  model: AnomalyDetectionJobModelResultModel
  signature: str


class ExecuteAnomalyDetectionJobResponse(NamedTuple):
  metaData: Optional[AnomalyDetection]
  model_result: Optional[AnomalyDetectionJobModelResult]
  table_result: Optional[DataFrame]
  logs: List[Logs]


class AnomalyDetectionResultsResponse(NamedTuple):
  metadata: Optional[AnomalyDetection]
  model_result: Optional[AnomalyDetectionJobModelResult]
  table_result: Optional[DataFrame]
  logs: List[Logs]


class AnomalyDetectionListPayload(TypedDict):
  experimentId: str
  useCaseId: str
  type: str
  parentId: str
  sort: str
  offset: int
  limit: int
