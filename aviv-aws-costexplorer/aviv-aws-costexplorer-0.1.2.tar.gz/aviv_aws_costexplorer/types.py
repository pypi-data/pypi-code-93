import typing

CAUTimePeriod = typing.Dict[typing.Literal['Start', 'End'], str]
CAUGranularity = typing.Literal['MONTHLY', 'DAILY', 'HOURLY']
CAUGroupByType = typing.Literal['DIMENSION', 'TAG', 'COST_CATEGORY']
CAUMetrics = typing.List[typing.Literal['AmortizedCost', 'BlendedCost', 'NetAmortizedCost', 'NetUnblendedCost', 'NormalizedUsageAmount', 'UnblendedCost', 'UsageQuantity']]

CAUDimensions = typing.Literal['RECORD_TYPE', 'SERVICE', 'REGION', 'LINKED_ACCOUNT']

# AWS CostExplorer API protos
CAUFilter = typing.Dict[typing.Literal['Or', 'And', 'Not'], dict]
CAUGroupBy = typing.List[typing.Dict[typing.Literal['Type', 'Key'], str]]


# Cleanup
MatchOptions = typing.Literal['EQUALS', 'STARTS_WITH', 'ENDS_WITH', 'CONTAINS', 'CASE_SENSITIVE', 'CASE_INSENSITIVE']
CAU_RECORD_TYPE = typing.Literal["Credit", "Refund", "Upfront", "Support"]
# RECORD_TYPE_DIMENSIONS = typing.List[typing.Literal["Credit", "Refund", "Upfront", "Support"]]

# Set to Max history time CAU
CAUDefaultPeriods = dict(
    HOURLY=dict(days=14),
    DAILY=dict(days=90),
    MONTHLY=dict(months=12)
)



class CostAndUsageAttributes:
    Granularity: CAUGranularity
    TimePeriod: CAUTimePeriod
    Filter: CAUFilter
    Metrics: CAUMetrics
    GroupBy: CAUGroupBy
    NextPageToken: str

    def __init__(self) -> None:
        pass
