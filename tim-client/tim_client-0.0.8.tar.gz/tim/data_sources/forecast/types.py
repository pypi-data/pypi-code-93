from pandas.core.frame import DataFrame
from enum import Enum
from typing import Any, List, Union, NamedTuple, Optional
from typing_extensions import TypedDict
from tim.types import Logs

Range = TypedDict('Range', {'from': str, 'to': str})


class Backtest(Enum):
  ALL = 'All'
  PRODUCTION = 'Production'
  OUT_OF_SAMPLE = 'OutOfSample'


class PredictionBoundariesType(Enum):
  EXPLICIT = 'Explicit'
  NONE = 'None'


class PredictionBoundaries(TypedDict):
  type: PredictionBoundariesType
  maxValue: float
  minValue: float


class Feature(Enum):
  EXPONENTIAL_MOVING_AVERAGE = 'ExponentialMovingAverage'
  SIMPLE_MOVING_AVERAGE = 'SimpleMovingAverage'
  REST_OF_WEEK = 'RestOfWeek'
  DAY_OF_WEEK = 'DayOfWeek'
  MONTH = 'Month'
  COS = 'Cos'
  SIN = 'Sin'
  FOURIER = 'Fourier'
  TREND = 'Trend'
  PERIODIC = 'Periodic'
  INTERCEPT = 'Intercept'
  PIECEWISE_LINEAR = 'PiecewiseLinear'
  TIME_OFFSETS = 'TimeOffsets'
  POLYNOMIAL = 'Polynomial'
  IDENTITY = 'Identity'
  PUBLIC_HOLIDAYS = 'PublicHolidays'


class BaseUnit(Enum):
  DAY = 'Day'
  HOUR = 'Hour'
  MINUTE = 'Minute'
  SECOND = 'Second'
  MONTH = 'Month'
  SAMPLE = 'Sample'


class ModelQuality(Enum):
  COMBINED = 'Combined'
  LOW = 'Low'
  MEDIUM = 'Medium'
  HIGH = 'High'
  VERYHIGH = 'VeryHigh'
  ULTRAHIGH = 'UltraHigh'


class RelativeRange(TypedDict):
  baseUnit: BaseUnit
  value: int


class ImputationType(Enum):
  LINEAR = 'Linear'
  LOCF = 'LOCF'
  NONE = 'None'


class Imputation(TypedDict):
  type: ImputationType
  maxGapLength: int


class Aggregation(Enum):
  MEAN = 'Mean'
  SUM = 'Sum'
  MINIMUM = 'Minumum'
  MAXIMUM = 'Maximum'


class Configuration(TypedDict, total=False):
  predictionTo: RelativeRange
  predictionFrom: RelativeRange
  modelQuality: ModelQuality
  normalization: bool
  maxModelComplexity: int
  features: List[Feature]
  dailyCycle: bool
  memoryLimitCheck: bool
  predictionIntervals: float
  predictionBoundaries: PredictionBoundaries
  rollingWindow: RelativeRange
  backtest: Backtest


class Data(TypedDict, total=False):
  versionId: str
  inSampleRows: Union[RelativeRange, List[Range]]
  outOfSampleRows: Union[RelativeRange, List[Range]]
  imputation: Imputation
  columns: List[Union[str, int]]
  targetColumn: Union[str, int]
  holidayColumn: Union[str, int]
  timeScale: RelativeRange
  aggregation: Aggregation


class ForecastJobConfiguration(TypedDict):
  name: str
  useCaseId: str
  configuration: Configuration
  data: Data


class CreateForecastConfiguration(TypedDict):
  name: str
  configuration: Configuration
  data: Data


class BuildModelResponse(TypedDict):
  id: str
  expectedResultsTableSize: float


class SampleMeasures(TypedDict):
  name: str
  inSample: str
  outOfSample: str


class ErrorMeasures(TypedDict):
  all: SampleMeasures
  bin: List[SampleMeasures]
  samplesAhead: List[SampleMeasures]


class ForecastJobType(Enum):
  BUILD_MODEL = 'build-model'
  REBUILD_MODEL = 'rebuild-model'
  RCA = 'rca'


class ForecastMetadata(TypedDict):
  id: str
  name: str
  type: ForecastJobType
  status: str
  parentId: str
  sequenceId: str
  useCaseId: str
  experimentId: str
  dataVersionId: str
  createdAt: str
  executedAt: str
  completedAt: str
  workerVersion: float
  errorMeasures: ErrorMeasures
  registrationBody: ForecastJobConfiguration


class ExecuteResponse(TypedDict):
  message: str
  code: str


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


class ModelZooModel(TypedDict):
  index: int
  terms: List[Term]
  dayTime: Any
  samplesAhead: List[int]
  modelQuality: int
  predictionIntervals: List[int]
  lastTargetTimestamp: str
  RInv: List[int]
  g: List[int]
  mx: List[int]


class VariableProperties(TypedDict):
  name: str
  importance: int


class ModelZoo(TypedDict):
  samplingPeriod: str
  originalSamplingPeriod: str
  averageTrainingLength: int
  models: List[ModelZooModel]
  difficulty: int
  targetName: str
  holidayName: str
  upperBoundary: int
  lowerBoundary: int
  dailyCycle: bool
  variableProperties: List[VariableProperties]


class Model(TypedDict):
  modelZoo: ModelZoo


class ForecastModelResult(TypedDict):
  modelVersion: str
  model: Model
  signature: str


class AccuracyMetrics(TypedDict):
  mape: float
  rmse: float
  accuracy: str
  mae: float


class ForecastAccuracies(TypedDict):
  all: SampleMeasures
  bin: List[SampleMeasures]
  samplesAhead: List[SampleMeasures]


class ExecuteForecastJobResponse(NamedTuple):
  metaData: Optional[ForecastMetadata]
  model_result: Optional[ForecastModelResult]
  table_result: Optional[DataFrame]
  accuracies: Optional[ForecastAccuracies]
  logs: List[Logs]


class ForecastResultsResponse(NamedTuple):
  metadata: Optional[ForecastMetadata]
  model_result: Optional[ForecastModelResult]
  table_result: Optional[DataFrame]
  accuracies: Optional[ForecastAccuracies]
  logs: List[Logs]


class ForecastTableRequestPayload(TypedDict):
  forecastType: Optional[str]
  modelIndex: Optional[int]
