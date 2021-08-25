# This code parses date/times, so please
#
#     pip install python-dateutil
#
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = metadata_change_event_from_dict(json.loads(json_string))

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, List, TypeVar, Type, Callable, cast
from datetime import datetime
import dateutil.parser


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class AspectType(Enum):
    DASHBOARD_INFO = "DASHBOARD_INFO"
    DASHBOARD_UPSTREAM = "DASHBOARD_UPSTREAM"
    DATASET_DOCUMENTATION = "DATASET_DOCUMENTATION"
    DATASET_SCHEMA = "DATASET_SCHEMA"
    DATASET_STATISTICS = "DATASET_STATISTICS"
    DATASET_UPSTREAM = "DATASET_UPSTREAM"
    DATASET_USAGE = "DATASET_USAGE"
    KNOWLEDGE_CARD_INFO = "KNOWLEDGE_CARD_INFO"
    KNOWLEDGE_CARD_VALIDATION = "KNOWLEDGE_CARD_VALIDATION"
    PERSON_ACTIVITY = "PERSON_ACTIVITY"
    PERSON_EDITABLE_INFO = "PERSON_EDITABLE_INFO"
    PERSON_ORGANIZATION = "PERSON_ORGANIZATION"
    PERSON_PROPERTIES = "PERSON_PROPERTIES"
    PERSON_SLACK_PROFILE = "PERSON_SLACK_PROFILE"
    PROPERTIES = "PROPERTIES"
    SUPPORT_INFO = "SUPPORT_INFO"


class ChartType(Enum):
    AREA = "AREA"
    BAR = "BAR"
    BOX_PLOT = "BOX_PLOT"
    COLUMN = "COLUMN"
    DONUT = "DONUT"
    FUNNEL = "FUNNEL"
    LINE = "LINE"
    MAP = "MAP"
    OTHER = "OTHER"
    PIE = "PIE"
    SCATTER = "SCATTER"
    TABLE = "TABLE"
    TEXT = "TEXT"
    TIMELINE = "TIMELINE"
    UNKNOWN = "UNKNOWN"
    WATERFALL = "WATERFALL"


@dataclass
class Chart:
    chart_type: Optional[ChartType] = None
    title: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Chart':
        assert isinstance(obj, dict)
        chart_type = from_union([ChartType, from_none], obj.get("chartType"))
        title = from_union([from_str, from_none], obj.get("title"))
        return Chart(chart_type, title)

    def to_dict(self) -> dict:
        result: dict = {}
        result["chartType"] = from_union([lambda x: to_enum(ChartType, x), from_none], self.chart_type)
        result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class ObjectID:
    """A class representation of the BSON ObjectId type."""
    """The generation time of this ObjectId instance"""
    generation_time: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ObjectID':
        assert isinstance(obj, dict)
        generation_time = from_union([from_float, from_none], obj.get("generationTime"))
        return ObjectID(generation_time)

    def to_dict(self) -> dict:
        result: dict = {}
        result["generationTime"] = from_union([to_float, from_none], self.generation_time)
        return result


@dataclass
class DashboardInfo:
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    charts: Optional[List[Chart]] = None
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    entity_id: Optional[str] = None
    dashboard_info_id: Optional[str] = None
    latest: Optional[bool] = None
    title: Optional[str] = None
    url: Optional[str] = None
    view_count: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DashboardInfo':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        charts = from_union([lambda x: from_list(Chart.from_dict, x), from_none], obj.get("charts"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        description = from_union([from_str, from_none], obj.get("description"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        dashboard_info_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        title = from_union([from_str, from_none], obj.get("title"))
        url = from_union([from_str, from_none], obj.get("url"))
        view_count = from_union([from_float, from_none], obj.get("viewCount"))
        return DashboardInfo(id, aspect_type, charts, created_at, description, entity_id, dashboard_info_id, latest, title, url, view_count)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["charts"] = from_union([lambda x: from_list(lambda x: to_class(Chart, x), x), from_none], self.charts)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["description"] = from_union([from_str, from_none], self.description)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.dashboard_info_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["title"] = from_union([from_str, from_none], self.title)
        result["url"] = from_union([from_str, from_none], self.url)
        result["viewCount"] = from_union([to_float, from_none], self.view_count)
        return result


class EntityType(Enum):
    DASHBOARD = "DASHBOARD"
    DATASET = "DATASET"
    KNOWLEDGE_CARD = "KNOWLEDGE_CARD"
    PERSON = "PERSON"


class DashboardPlatform(Enum):
    LOOKER = "LOOKER"
    UNKNOWN = "UNKNOWN"


@dataclass
class DashboardLogicalID:
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    dashboard_id: Optional[str] = None
    platform: Optional[DashboardPlatform] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DashboardLogicalID':
        assert isinstance(obj, dict)
        dashboard_id = from_union([from_str, from_none], obj.get("dashboardId"))
        platform = from_union([DashboardPlatform, from_none], obj.get("platform"))
        return DashboardLogicalID(dashboard_id, platform)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dashboardId"] = from_union([from_str, from_none], self.dashboard_id)
        result["platform"] = from_union([lambda x: to_enum(DashboardPlatform, x), from_none], self.platform)
        return result


@dataclass
class DashboardUpstream:
    """DashboardUpstream captures upstream lineages from data sources to this dashboard"""
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    dashboard_upstream_id: Optional[str] = None
    latest: Optional[bool] = None
    source_datasets: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DashboardUpstream':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        dashboard_upstream_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        source_datasets = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceDatasets"))
        return DashboardUpstream(id, aspect_type, created_at, entity_id, dashboard_upstream_id, latest, source_datasets)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.dashboard_upstream_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["sourceDatasets"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_datasets)
        return result


@dataclass
class Dashboard:
    """Backing store for an optionally provided creation date"""
    created_at: Optional[datetime] = None
    """A class representation of the BSON ObjectId type."""
    id: Optional[ObjectID] = None
    dashboard_created_at: Optional[datetime] = None
    dashboard_info: Optional[DashboardInfo] = None
    deleted_at: Optional[datetime] = None
    entity_type: Optional[EntityType] = None
    """A getter for the id property that's directly generated from the
    entity type & logical ID.
    """
    dashboard_id: Optional[str] = None
    last_modified_at: Optional[datetime] = None
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    logical_id: Optional[DashboardLogicalID] = None
    """DashboardUpstream captures upstream lineages from data sources to this dashboard"""
    upstream: Optional[DashboardUpstream] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Dashboard':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        dashboard_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        dashboard_info = from_union([DashboardInfo.from_dict, from_none], obj.get("dashboardInfo"))
        deleted_at = from_union([from_datetime, from_none], obj.get("deletedAt"))
        entity_type = from_union([EntityType, from_none], obj.get("entityType"))
        dashboard_id = from_union([from_str, from_none], obj.get("id"))
        last_modified_at = from_union([from_datetime, from_none], obj.get("lastModifiedAt"))
        logical_id = from_union([DashboardLogicalID.from_dict, from_none], obj.get("logicalId"))
        upstream = from_union([DashboardUpstream.from_dict, from_none], obj.get("upstream"))
        return Dashboard(created_at, id, dashboard_created_at, dashboard_info, deleted_at, entity_type, dashboard_id, last_modified_at, logical_id, upstream)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dashboard_created_at)
        result["dashboardInfo"] = from_union([lambda x: to_class(DashboardInfo, x), from_none], self.dashboard_info)
        result["deletedAt"] = from_union([lambda x: x.isoformat(), from_none], self.deleted_at)
        result["entityType"] = from_union([lambda x: to_enum(EntityType, x), from_none], self.entity_type)
        result["id"] = from_union([from_str, from_none], self.dashboard_id)
        result["lastModifiedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_modified_at)
        result["logicalId"] = from_union([lambda x: to_class(DashboardLogicalID, x), from_none], self.logical_id)
        result["upstream"] = from_union([lambda x: to_class(DashboardUpstream, x), from_none], self.upstream)
        return result


@dataclass
class FieldDocumentation:
    documentation: Optional[str] = None
    field_path: Optional[str] = None
    tests: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FieldDocumentation':
        assert isinstance(obj, dict)
        documentation = from_union([from_str, from_none], obj.get("documentation"))
        field_path = from_union([from_str, from_none], obj.get("fieldPath"))
        tests = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tests"))
        return FieldDocumentation(documentation, field_path, tests)

    def to_dict(self) -> dict:
        result: dict = {}
        result["documentation"] = from_union([from_str, from_none], self.documentation)
        result["fieldPath"] = from_union([from_str, from_none], self.field_path)
        result["tests"] = from_union([lambda x: from_list(from_str, x), from_none], self.tests)
        return result


@dataclass
class DatasetDocumentation:
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    dataset_documentations: Optional[List[str]] = None
    entity_id: Optional[str] = None
    field_documentations: Optional[List[FieldDocumentation]] = None
    dataset_documentation_id: Optional[str] = None
    latest: Optional[bool] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetDocumentation':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        dataset_documentations = from_union([lambda x: from_list(from_str, x), from_none], obj.get("datasetDocumentations"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        field_documentations = from_union([lambda x: from_list(FieldDocumentation.from_dict, x), from_none], obj.get("fieldDocumentations"))
        dataset_documentation_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        return DatasetDocumentation(id, aspect_type, created_at, dataset_documentations, entity_id, field_documentations, dataset_documentation_id, latest)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["datasetDocumentations"] = from_union([lambda x: from_list(from_str, x), from_none], self.dataset_documentations)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["fieldDocumentations"] = from_union([lambda x: from_list(lambda x: to_class(FieldDocumentation, x), x), from_none], self.field_documentations)
        result["id"] = from_union([from_str, from_none], self.dataset_documentation_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        return result


class DataPlatform(Enum):
    BIGQUERY = "BIGQUERY"
    DOCUMENTDB = "DOCUMENTDB"
    DYNAMODB = "DYNAMODB"
    ELASTICSEARCH = "ELASTICSEARCH"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    RDS = "RDS"
    REDIS = "REDIS"
    REDSHIFT = "REDSHIFT"
    S3 = "S3"
    SNOWFLAKE = "SNOWFLAKE"
    UNKNOWN = "UNKNOWN"


@dataclass
class DatasetLogicalID:
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    name: Optional[str] = None
    platform: Optional[DataPlatform] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetLogicalID':
        assert isinstance(obj, dict)
        name = from_union([from_str, from_none], obj.get("name"))
        platform = from_union([DataPlatform, from_none], obj.get("platform"))
        return DatasetLogicalID(name, platform)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_union([from_str, from_none], self.name)
        result["platform"] = from_union([lambda x: to_enum(DataPlatform, x), from_none], self.platform)
        return result


@dataclass
class AuditStamp:
    actor: Optional[str] = None
    time: Optional[datetime] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AuditStamp':
        assert isinstance(obj, dict)
        actor = from_union([from_str, from_none], obj.get("actor"))
        time = from_union([from_datetime, from_none], obj.get("time"))
        return AuditStamp(actor, time)

    def to_dict(self) -> dict:
        result: dict = {}
        result["actor"] = from_union([from_str, from_none], self.actor)
        result["time"] = from_union([lambda x: x.isoformat(), from_none], self.time)
        return result


@dataclass
class Deprecation:
    deprecated_by: Optional[AuditStamp] = None
    reason: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Deprecation':
        assert isinstance(obj, dict)
        deprecated_by = from_union([AuditStamp.from_dict, from_none], obj.get("deprecatedBy"))
        reason = from_union([from_str, from_none], obj.get("reason"))
        return Deprecation(deprecated_by, reason)

    def to_dict(self) -> dict:
        result: dict = {}
        result["deprecatedBy"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.deprecated_by)
        result["reason"] = from_union([from_str, from_none], self.reason)
        return result


@dataclass
class Properties:
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    deprecated: Optional[Deprecation] = None
    description: Optional[str] = None
    entity_id: Optional[str] = None
    properties_id: Optional[str] = None
    latest: Optional[bool] = None
    tags: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Properties':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        deprecated = from_union([Deprecation.from_dict, from_none], obj.get("deprecated"))
        description = from_union([from_str, from_none], obj.get("description"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        properties_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        tags = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tags"))
        return Properties(id, aspect_type, created_at, deprecated, description, entity_id, properties_id, latest, tags)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["deprecated"] = from_union([lambda x: to_class(Deprecation, x), from_none], self.deprecated)
        result["description"] = from_union([from_str, from_none], self.description)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.properties_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["tags"] = from_union([lambda x: from_list(from_str, x), from_none], self.tags)
        return result


@dataclass
class SchemaField:
    description: Optional[str] = None
    field_path: Optional[str] = None
    native_type: Optional[str] = None
    nullable: Optional[bool] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SchemaField':
        assert isinstance(obj, dict)
        description = from_union([from_str, from_none], obj.get("description"))
        field_path = from_union([from_str, from_none], obj.get("fieldPath"))
        native_type = from_union([from_str, from_none], obj.get("nativeType"))
        nullable = from_union([from_bool, from_none], obj.get("nullable"))
        return SchemaField(description, field_path, native_type, nullable)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_union([from_str, from_none], self.description)
        result["fieldPath"] = from_union([from_str, from_none], self.field_path)
        result["nativeType"] = from_union([from_str, from_none], self.native_type)
        result["nullable"] = from_union([from_bool, from_none], self.nullable)
        return result


class SchemaType(Enum):
    AVRO = "AVRO"
    DYNAMODB = "DYNAMODB"
    JSON = "JSON"
    ORC = "ORC"
    PARQUET = "PARQUET"
    PROTOBUF = "PROTOBUF"
    SCHEMALESS = "SCHEMALESS"
    SQL = "SQL"


@dataclass
class ForeignKey:
    field_path: Optional[str] = None
    parent: Optional[DatasetLogicalID] = None
    parent_field: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ForeignKey':
        assert isinstance(obj, dict)
        field_path = from_union([from_str, from_none], obj.get("fieldPath"))
        parent = from_union([DatasetLogicalID.from_dict, from_none], obj.get("parent"))
        parent_field = from_union([from_str, from_none], obj.get("parentField"))
        return ForeignKey(field_path, parent, parent_field)

    def to_dict(self) -> dict:
        result: dict = {}
        result["fieldPath"] = from_union([from_str, from_none], self.field_path)
        result["parent"] = from_union([lambda x: to_class(DatasetLogicalID, x), from_none], self.parent)
        result["parentField"] = from_union([from_str, from_none], self.parent_field)
        return result


class MaterializationType(Enum):
    EXTERNAL = "EXTERNAL"
    MATERIALIZED_VIEW = "MATERIALIZED_VIEW"
    TABLE = "TABLE"
    VIEW = "VIEW"


@dataclass
class SQLSchema:
    foreign_key: Optional[List[ForeignKey]] = None
    materialization: Optional[MaterializationType] = None
    primary_key: Optional[List[str]] = None
    table_schema: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SQLSchema':
        assert isinstance(obj, dict)
        foreign_key = from_union([lambda x: from_list(ForeignKey.from_dict, x), from_none], obj.get("foreignKey"))
        materialization = from_union([MaterializationType, from_none], obj.get("materialization"))
        primary_key = from_union([lambda x: from_list(from_str, x), from_none], obj.get("primaryKey"))
        table_schema = from_union([from_str, from_none], obj.get("tableSchema"))
        return SQLSchema(foreign_key, materialization, primary_key, table_schema)

    def to_dict(self) -> dict:
        result: dict = {}
        result["foreignKey"] = from_union([lambda x: from_list(lambda x: to_class(ForeignKey, x), x), from_none], self.foreign_key)
        result["materialization"] = from_union([lambda x: to_enum(MaterializationType, x), from_none], self.materialization)
        result["primaryKey"] = from_union([lambda x: from_list(from_str, x), from_none], self.primary_key)
        result["tableSchema"] = from_union([from_str, from_none], self.table_schema)
        return result


@dataclass
class DatasetSchema:
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    entity_id: Optional[str] = None
    fields: Optional[List[SchemaField]] = None
    dataset_schema_id: Optional[str] = None
    last_modified: Optional[AuditStamp] = None
    latest: Optional[bool] = None
    schema_type: Optional[SchemaType] = None
    sql_schema: Optional[SQLSchema] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetSchema':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        description = from_union([from_str, from_none], obj.get("description"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        fields = from_union([lambda x: from_list(SchemaField.from_dict, x), from_none], obj.get("fields"))
        dataset_schema_id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        schema_type = from_union([SchemaType, from_none], obj.get("schemaType"))
        sql_schema = from_union([SQLSchema.from_dict, from_none], obj.get("sqlSchema"))
        return DatasetSchema(id, aspect_type, created_at, description, entity_id, fields, dataset_schema_id, last_modified, latest, schema_type, sql_schema)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["description"] = from_union([from_str, from_none], self.description)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["fields"] = from_union([lambda x: from_list(lambda x: to_class(SchemaField, x), x), from_none], self.fields)
        result["id"] = from_union([from_str, from_none], self.dataset_schema_id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["schemaType"] = from_union([lambda x: to_enum(SchemaType, x), from_none], self.schema_type)
        result["sqlSchema"] = from_union([lambda x: to_class(SQLSchema, x), from_none], self.sql_schema)
        return result


@dataclass
class DatasetStatistics:
    """DatasetStatistics captures operational information about the dataset, e.g. the number of
    records or the last refresh time.
    """
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    data_size: Optional[float] = None
    entity_id: Optional[str] = None
    dataset_statistics_id: Optional[str] = None
    last_updated: Optional[datetime] = None
    latest: Optional[bool] = None
    record_count: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetStatistics':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        data_size = from_union([from_float, from_none], obj.get("dataSize"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        dataset_statistics_id = from_union([from_str, from_none], obj.get("id"))
        last_updated = from_union([from_datetime, from_none], obj.get("lastUpdated"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        record_count = from_union([from_float, from_none], obj.get("recordCount"))
        return DatasetStatistics(id, aspect_type, created_at, data_size, entity_id, dataset_statistics_id, last_updated, latest, record_count)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["dataSize"] = from_union([to_float, from_none], self.data_size)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.dataset_statistics_id)
        result["lastUpdated"] = from_union([lambda x: x.isoformat(), from_none], self.last_updated)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["recordCount"] = from_union([to_float, from_none], self.record_count)
        return result


@dataclass
class ChannelSlackInfo:
    channel_id: Optional[str] = None
    is_archived: Optional[bool] = None
    name: Optional[str] = None
    purpose: Optional[str] = None
    team_id: Optional[str] = None
    topic: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ChannelSlackInfo':
        assert isinstance(obj, dict)
        channel_id = from_union([from_str, from_none], obj.get("channelId"))
        is_archived = from_union([from_bool, from_none], obj.get("isArchived"))
        name = from_union([from_str, from_none], obj.get("name"))
        purpose = from_union([from_str, from_none], obj.get("purpose"))
        team_id = from_union([from_str, from_none], obj.get("teamId"))
        topic = from_union([from_str, from_none], obj.get("topic"))
        return ChannelSlackInfo(channel_id, is_archived, name, purpose, team_id, topic)

    def to_dict(self) -> dict:
        result: dict = {}
        result["channelId"] = from_union([from_str, from_none], self.channel_id)
        result["isArchived"] = from_union([from_bool, from_none], self.is_archived)
        result["name"] = from_union([from_str, from_none], self.name)
        result["purpose"] = from_union([from_str, from_none], self.purpose)
        result["teamId"] = from_union([from_str, from_none], self.team_id)
        result["topic"] = from_union([from_str, from_none], self.topic)
        return result


@dataclass
class SupportInfo:
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    email: Optional[str] = None
    entity_id: Optional[str] = None
    support_info_id: Optional[str] = None
    latest: Optional[bool] = None
    slack_info: Optional[ChannelSlackInfo] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SupportInfo':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        email = from_union([from_str, from_none], obj.get("email"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        support_info_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        slack_info = from_union([ChannelSlackInfo.from_dict, from_none], obj.get("slackInfo"))
        return SupportInfo(id, aspect_type, created_at, email, entity_id, support_info_id, latest, slack_info)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["email"] = from_union([from_str, from_none], self.email)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.support_info_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["slackInfo"] = from_union([lambda x: to_class(ChannelSlackInfo, x), from_none], self.slack_info)
        return result


@dataclass
class DatasetField:
    dataset: Optional[DatasetLogicalID] = None
    field: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetField':
        assert isinstance(obj, dict)
        dataset = from_union([DatasetLogicalID.from_dict, from_none], obj.get("dataset"))
        field = from_union([from_str, from_none], obj.get("field"))
        return DatasetField(dataset, field)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dataset"] = from_union([lambda x: to_class(DatasetLogicalID, x), from_none], self.dataset)
        result["field"] = from_union([from_str, from_none], self.field)
        return result


@dataclass
class FieldMapping:
    destination: Optional[str] = None
    sources: Optional[List[DatasetField]] = None
    transformation: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FieldMapping':
        assert isinstance(obj, dict)
        destination = from_union([from_str, from_none], obj.get("destination"))
        sources = from_union([lambda x: from_list(DatasetField.from_dict, x), from_none], obj.get("sources"))
        transformation = from_union([from_str, from_none], obj.get("transformation"))
        return FieldMapping(destination, sources, transformation)

    def to_dict(self) -> dict:
        result: dict = {}
        result["destination"] = from_union([from_str, from_none], self.destination)
        result["sources"] = from_union([lambda x: from_list(lambda x: to_class(DatasetField, x), x), from_none], self.sources)
        result["transformation"] = from_union([from_str, from_none], self.transformation)
        return result


@dataclass
class DatasetUpstream:
    """DatasetUpstream captures upstream lineages from data sources to this dataset"""
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    executor_url: Optional[str] = None
    field_mappings: Optional[List[FieldMapping]] = None
    dataset_upstream_id: Optional[str] = None
    latest: Optional[bool] = None
    source_code_url: Optional[str] = None
    source_datasets: Optional[List[str]] = None
    transformation: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetUpstream':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        executor_url = from_union([from_str, from_none], obj.get("executorUrl"))
        field_mappings = from_union([lambda x: from_list(FieldMapping.from_dict, x), from_none], obj.get("fieldMappings"))
        dataset_upstream_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        source_code_url = from_union([from_str, from_none], obj.get("sourceCodeUrl"))
        source_datasets = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sourceDatasets"))
        transformation = from_union([from_str, from_none], obj.get("transformation"))
        return DatasetUpstream(id, aspect_type, created_at, entity_id, executor_url, field_mappings, dataset_upstream_id, latest, source_code_url, source_datasets, transformation)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["executorUrl"] = from_union([from_str, from_none], self.executor_url)
        result["fieldMappings"] = from_union([lambda x: from_list(lambda x: to_class(FieldMapping, x), x), from_none], self.field_mappings)
        result["id"] = from_union([from_str, from_none], self.dataset_upstream_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["sourceCodeUrl"] = from_union([from_str, from_none], self.source_code_url)
        result["sourceDatasets"] = from_union([lambda x: from_list(from_str, x), from_none], self.source_datasets)
        result["transformation"] = from_union([from_str, from_none], self.transformation)
        return result


@dataclass
class FieldQueryCount:
    """Query count number and statistics"""
    count: Optional[float] = None
    field: Optional[str] = None
    percentile: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FieldQueryCount':
        assert isinstance(obj, dict)
        count = from_union([from_float, from_none], obj.get("count"))
        field = from_union([from_str, from_none], obj.get("field"))
        percentile = from_union([from_float, from_none], obj.get("percentile"))
        return FieldQueryCount(count, field, percentile)

    def to_dict(self) -> dict:
        result: dict = {}
        result["count"] = from_union([to_float, from_none], self.count)
        result["field"] = from_union([from_str, from_none], self.field)
        result["percentile"] = from_union([to_float, from_none], self.percentile)
        return result


@dataclass
class FieldQueryCounts:
    """Captures field/column query counts in last day/week/month/year."""
    last24_hours: Optional[List[FieldQueryCount]] = None
    last30_days: Optional[List[FieldQueryCount]] = None
    last365_days: Optional[List[FieldQueryCount]] = None
    last7_days: Optional[List[FieldQueryCount]] = None
    last90_days: Optional[List[FieldQueryCount]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FieldQueryCounts':
        assert isinstance(obj, dict)
        last24_hours = from_union([lambda x: from_list(FieldQueryCount.from_dict, x), from_none], obj.get("last24Hours"))
        last30_days = from_union([lambda x: from_list(FieldQueryCount.from_dict, x), from_none], obj.get("last30Days"))
        last365_days = from_union([lambda x: from_list(FieldQueryCount.from_dict, x), from_none], obj.get("last365Days"))
        last7_days = from_union([lambda x: from_list(FieldQueryCount.from_dict, x), from_none], obj.get("last7Days"))
        last90_days = from_union([lambda x: from_list(FieldQueryCount.from_dict, x), from_none], obj.get("last90Days"))
        return FieldQueryCounts(last24_hours, last30_days, last365_days, last7_days, last90_days)

    def to_dict(self) -> dict:
        result: dict = {}
        result["last24Hours"] = from_union([lambda x: from_list(lambda x: to_class(FieldQueryCount, x), x), from_none], self.last24_hours)
        result["last30Days"] = from_union([lambda x: from_list(lambda x: to_class(FieldQueryCount, x), x), from_none], self.last30_days)
        result["last365Days"] = from_union([lambda x: from_list(lambda x: to_class(FieldQueryCount, x), x), from_none], self.last365_days)
        result["last7Days"] = from_union([lambda x: from_list(lambda x: to_class(FieldQueryCount, x), x), from_none], self.last7_days)
        result["last90Days"] = from_union([lambda x: from_list(lambda x: to_class(FieldQueryCount, x), x), from_none], self.last90_days)
        return result


@dataclass
class QueryCount:
    """Query count number and statistics"""
    count: Optional[float] = None
    percentile: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'QueryCount':
        assert isinstance(obj, dict)
        count = from_union([from_float, from_none], obj.get("count"))
        percentile = from_union([from_float, from_none], obj.get("percentile"))
        return QueryCount(count, percentile)

    def to_dict(self) -> dict:
        result: dict = {}
        result["count"] = from_union([to_float, from_none], self.count)
        result["percentile"] = from_union([to_float, from_none], self.percentile)
        return result


@dataclass
class QueryCounts:
    """Captures query counts in last day/week/month/year."""
    """Query count number and statistics"""
    last24_hours: Optional[QueryCount] = None
    """Query count number and statistics"""
    last30_days: Optional[QueryCount] = None
    """Query count number and statistics"""
    last365_days: Optional[QueryCount] = None
    """Query count number and statistics"""
    last7_days: Optional[QueryCount] = None
    """Query count number and statistics"""
    last90_days: Optional[QueryCount] = None

    @staticmethod
    def from_dict(obj: Any) -> 'QueryCounts':
        assert isinstance(obj, dict)
        last24_hours = from_union([QueryCount.from_dict, from_none], obj.get("last24Hours"))
        last30_days = from_union([QueryCount.from_dict, from_none], obj.get("last30Days"))
        last365_days = from_union([QueryCount.from_dict, from_none], obj.get("last365Days"))
        last7_days = from_union([QueryCount.from_dict, from_none], obj.get("last7Days"))
        last90_days = from_union([QueryCount.from_dict, from_none], obj.get("last90Days"))
        return QueryCounts(last24_hours, last30_days, last365_days, last7_days, last90_days)

    def to_dict(self) -> dict:
        result: dict = {}
        result["last24Hours"] = from_union([lambda x: to_class(QueryCount, x), from_none], self.last24_hours)
        result["last30Days"] = from_union([lambda x: to_class(QueryCount, x), from_none], self.last30_days)
        result["last365Days"] = from_union([lambda x: to_class(QueryCount, x), from_none], self.last365_days)
        result["last7Days"] = from_union([lambda x: to_class(QueryCount, x), from_none], self.last7_days)
        result["last90Days"] = from_union([lambda x: to_class(QueryCount, x), from_none], self.last90_days)
        return result


@dataclass
class DatasetUsage:
    """Captures dataset usage statistic, e.g. the query counts."""
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    field_query_counts: Optional[FieldQueryCounts] = None
    dataset_usage_id: Optional[str] = None
    latest: Optional[bool] = None
    query_counts: Optional[QueryCounts] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DatasetUsage':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        field_query_counts = from_union([FieldQueryCounts.from_dict, from_none], obj.get("fieldQueryCounts"))
        dataset_usage_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        query_counts = from_union([QueryCounts.from_dict, from_none], obj.get("queryCounts"))
        return DatasetUsage(id, aspect_type, created_at, entity_id, field_query_counts, dataset_usage_id, latest, query_counts)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["fieldQueryCounts"] = from_union([lambda x: to_class(FieldQueryCounts, x), from_none], self.field_query_counts)
        result["id"] = from_union([from_str, from_none], self.dataset_usage_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["queryCounts"] = from_union([lambda x: to_class(QueryCounts, x), from_none], self.query_counts)
        return result


@dataclass
class Dataset:
    """Backing store for an optionally provided creation date"""
    created_at: Optional[datetime] = None
    """A class representation of the BSON ObjectId type."""
    id: Optional[ObjectID] = None
    dataset_created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    documentation: Optional[DatasetDocumentation] = None
    entity_type: Optional[EntityType] = None
    """A getter for the id property that's directly generated from the
    entity type & logical ID.
    """
    dataset_id: Optional[str] = None
    last_modified_at: Optional[datetime] = None
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    logical_id: Optional[DatasetLogicalID] = None
    properties: Optional[Properties] = None
    schema: Optional[DatasetSchema] = None
    """DatasetStatistics captures operational information about the dataset, e.g. the number of
    records or the last refresh time.
    """
    statistics: Optional[DatasetStatistics] = None
    support_info: Optional[SupportInfo] = None
    """DatasetUpstream captures upstream lineages from data sources to this dataset"""
    upstream: Optional[DatasetUpstream] = None
    """Captures dataset usage statistic, e.g. the query counts."""
    usage: Optional[DatasetUsage] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Dataset':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        dataset_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        deleted_at = from_union([from_datetime, from_none], obj.get("deletedAt"))
        documentation = from_union([DatasetDocumentation.from_dict, from_none], obj.get("documentation"))
        entity_type = from_union([EntityType, from_none], obj.get("entityType"))
        dataset_id = from_union([from_str, from_none], obj.get("id"))
        last_modified_at = from_union([from_datetime, from_none], obj.get("lastModifiedAt"))
        logical_id = from_union([DatasetLogicalID.from_dict, from_none], obj.get("logicalId"))
        properties = from_union([Properties.from_dict, from_none], obj.get("properties"))
        schema = from_union([DatasetSchema.from_dict, from_none], obj.get("schema"))
        statistics = from_union([DatasetStatistics.from_dict, from_none], obj.get("statistics"))
        support_info = from_union([SupportInfo.from_dict, from_none], obj.get("supportInfo"))
        upstream = from_union([DatasetUpstream.from_dict, from_none], obj.get("upstream"))
        usage = from_union([DatasetUsage.from_dict, from_none], obj.get("usage"))
        return Dataset(created_at, id, dataset_created_at, deleted_at, documentation, entity_type, dataset_id, last_modified_at, logical_id, properties, schema, statistics, support_info, upstream, usage)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.dataset_created_at)
        result["deletedAt"] = from_union([lambda x: x.isoformat(), from_none], self.deleted_at)
        result["documentation"] = from_union([lambda x: to_class(DatasetDocumentation, x), from_none], self.documentation)
        result["entityType"] = from_union([lambda x: to_enum(EntityType, x), from_none], self.entity_type)
        result["id"] = from_union([from_str, from_none], self.dataset_id)
        result["lastModifiedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_modified_at)
        result["logicalId"] = from_union([lambda x: to_class(DatasetLogicalID, x), from_none], self.logical_id)
        result["properties"] = from_union([lambda x: to_class(Properties, x), from_none], self.properties)
        result["schema"] = from_union([lambda x: to_class(DatasetSchema, x), from_none], self.schema)
        result["statistics"] = from_union([lambda x: to_class(DatasetStatistics, x), from_none], self.statistics)
        result["supportInfo"] = from_union([lambda x: to_class(SupportInfo, x), from_none], self.support_info)
        result["upstream"] = from_union([lambda x: to_class(DatasetUpstream, x), from_none], self.upstream)
        result["usage"] = from_union([lambda x: to_class(DatasetUsage, x), from_none], self.usage)
        return result


@dataclass
class EventHeader:
    app_name: Optional[str] = None
    server: Optional[str] = None
    time: Optional[datetime] = None

    @staticmethod
    def from_dict(obj: Any) -> 'EventHeader':
        assert isinstance(obj, dict)
        app_name = from_union([from_str, from_none], obj.get("appName"))
        server = from_union([from_str, from_none], obj.get("server"))
        time = from_union([from_datetime, from_none], obj.get("time"))
        return EventHeader(app_name, server, time)

    def to_dict(self) -> dict:
        result: dict = {}
        result["appName"] = from_union([from_str, from_none], self.app_name)
        result["server"] = from_union([from_str, from_none], self.server)
        result["time"] = from_union([lambda x: x.isoformat(), from_none], self.time)
        return result


@dataclass
class BusinessCriticalTokenizedContent:
    justification: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'BusinessCriticalTokenizedContent':
        assert isinstance(obj, dict)
        justification = from_union([from_str, from_none], obj.get("justification"))
        return BusinessCriticalTokenizedContent(justification)

    def to_dict(self) -> dict:
        result: dict = {}
        result["justification"] = from_union([from_str, from_none], self.justification)
        return result


@dataclass
class BusinessCriticalKnowledgeCard:
    justification: Optional[str] = None
    tokenized_content: Optional[BusinessCriticalTokenizedContent] = None

    @staticmethod
    def from_dict(obj: Any) -> 'BusinessCriticalKnowledgeCard':
        assert isinstance(obj, dict)
        justification = from_union([from_str, from_none], obj.get("justification"))
        tokenized_content = from_union([BusinessCriticalTokenizedContent.from_dict, from_none], obj.get("tokenizedContent"))
        return BusinessCriticalKnowledgeCard(justification, tokenized_content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["justification"] = from_union([from_str, from_none], self.justification)
        result["tokenizedContent"] = from_union([lambda x: to_class(BusinessCriticalTokenizedContent, x), from_none], self.tokenized_content)
        return result


@dataclass
class DeprecationTokenizedContent:
    detail: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DeprecationTokenizedContent':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        return DeprecationTokenizedContent(detail)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        return result


@dataclass
class DeprecationKnowledgeCard:
    detail: Optional[str] = None
    planned_date: Optional[datetime] = None
    tokenized_content: Optional[DeprecationTokenizedContent] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DeprecationKnowledgeCard':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        planned_date = from_union([from_datetime, from_none], obj.get("plannedDate"))
        tokenized_content = from_union([DeprecationTokenizedContent.from_dict, from_none], obj.get("tokenizedContent"))
        return DeprecationKnowledgeCard(detail, planned_date, tokenized_content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        result["plannedDate"] = from_union([lambda x: x.isoformat(), from_none], self.planned_date)
        result["tokenizedContent"] = from_union([lambda x: to_class(DeprecationTokenizedContent, x), from_none], self.tokenized_content)
        return result


@dataclass
class IncidentTokenizedContent:
    detail: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'IncidentTokenizedContent':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        return IncidentTokenizedContent(detail)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        return result


@dataclass
class IncidentKnowledgeCard:
    detail: Optional[str] = None
    title: Optional[str] = None
    tokenized_content: Optional[IncidentTokenizedContent] = None

    @staticmethod
    def from_dict(obj: Any) -> 'IncidentKnowledgeCard':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        title = from_union([from_str, from_none], obj.get("title"))
        tokenized_content = from_union([IncidentTokenizedContent.from_dict, from_none], obj.get("tokenizedContent"))
        return IncidentKnowledgeCard(detail, title, tokenized_content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        result["title"] = from_union([from_str, from_none], self.title)
        result["tokenizedContent"] = from_union([lambda x: to_class(IncidentTokenizedContent, x), from_none], self.tokenized_content)
        return result


class KnowledgeCardType(Enum):
    BUSINESS_CRITICAL = "BUSINESS_CRITICAL"
    DEPRECATION = "DEPRECATION"
    HOW_TO_USE = "HOW_TO_USE"
    INCIDENT = "INCIDENT"
    UNKNOWN = "UNKNOWN"


@dataclass
class HowToUseTokenizedContent:
    detail: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'HowToUseTokenizedContent':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        return HowToUseTokenizedContent(detail)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        return result


@dataclass
class UsageKnowledgeCard:
    detail: Optional[str] = None
    example: Optional[str] = None
    title: Optional[str] = None
    tokenized_content: Optional[HowToUseTokenizedContent] = None

    @staticmethod
    def from_dict(obj: Any) -> 'UsageKnowledgeCard':
        assert isinstance(obj, dict)
        detail = from_union([from_str, from_none], obj.get("detail"))
        example = from_union([from_str, from_none], obj.get("example"))
        title = from_union([from_str, from_none], obj.get("title"))
        tokenized_content = from_union([HowToUseTokenizedContent.from_dict, from_none], obj.get("tokenizedContent"))
        return UsageKnowledgeCard(detail, example, title, tokenized_content)

    def to_dict(self) -> dict:
        result: dict = {}
        result["detail"] = from_union([from_str, from_none], self.detail)
        result["example"] = from_union([from_str, from_none], self.example)
        result["title"] = from_union([from_str, from_none], self.title)
        result["tokenizedContent"] = from_union([lambda x: to_class(HowToUseTokenizedContent, x), from_none], self.tokenized_content)
        return result


@dataclass
class KnowledgeCardDetail:
    """Collection of possible knowledge card types"""
    business_critical: Optional[BusinessCriticalKnowledgeCard] = None
    deprecation: Optional[DeprecationKnowledgeCard] = None
    incident: Optional[IncidentKnowledgeCard] = None
    type: Optional[KnowledgeCardType] = None
    usage: Optional[UsageKnowledgeCard] = None

    @staticmethod
    def from_dict(obj: Any) -> 'KnowledgeCardDetail':
        assert isinstance(obj, dict)
        business_critical = from_union([BusinessCriticalKnowledgeCard.from_dict, from_none], obj.get("businessCritical"))
        deprecation = from_union([DeprecationKnowledgeCard.from_dict, from_none], obj.get("deprecation"))
        incident = from_union([IncidentKnowledgeCard.from_dict, from_none], obj.get("incident"))
        type = from_union([KnowledgeCardType, from_none], obj.get("type"))
        usage = from_union([UsageKnowledgeCard.from_dict, from_none], obj.get("usage"))
        return KnowledgeCardDetail(business_critical, deprecation, incident, type, usage)

    def to_dict(self) -> dict:
        result: dict = {}
        result["businessCritical"] = from_union([lambda x: to_class(BusinessCriticalKnowledgeCard, x), from_none], self.business_critical)
        result["deprecation"] = from_union([lambda x: to_class(DeprecationKnowledgeCard, x), from_none], self.deprecation)
        result["incident"] = from_union([lambda x: to_class(IncidentKnowledgeCard, x), from_none], self.incident)
        result["type"] = from_union([lambda x: to_enum(KnowledgeCardType, x), from_none], self.type)
        result["usage"] = from_union([lambda x: to_class(UsageKnowledgeCard, x), from_none], self.usage)
        return result


@dataclass
class Hashtag:
    value: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Hashtag':
        assert isinstance(obj, dict)
        value = from_union([from_str, from_none], obj.get("value"))
        return Hashtag(value)

    def to_dict(self) -> dict:
        result: dict = {}
        result["value"] = from_union([from_str, from_none], self.value)
        return result


@dataclass
class KnowledgeCardInfo:
    id: Optional[ObjectID] = None
    """backing store for related Entities which contains
    related entity ids excluding the anchor Entity id
    Note: Cannot be a native private field since it's shared between input and output
    """
    non_anchoring_ids_backing_store: Optional[List[str]] = None
    """The global id for the Entity the associated Knowledge Card was created for. Must be
    provided on Knowledge Card creation
    Specified on the Input Type KnowledgeCardInfoInput
    """
    anchor_entity_id: Optional[str] = None
    archived: Optional[AuditStamp] = None
    aspect_type: Optional[AspectType] = None
    created: Optional[AuditStamp] = None
    created_at: Optional[datetime] = None
    detail: Optional[KnowledgeCardDetail] = None
    entity_id: Optional[str] = None
    hashtags: Optional[List[Hashtag]] = None
    knowledge_card_info_id: Optional[str] = None
    last_modified: Optional[AuditStamp] = None
    latest: Optional[bool] = None
    """Getter and setter interface to protected _nonAnchoringIdsBackingStore
    Includes the non-empty anchorEntityId as the first item in the list
    of relatedEntityIds
    """
    related_entity_ids: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'KnowledgeCardInfo':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        non_anchoring_ids_backing_store = from_union([lambda x: from_list(from_str, x), from_none], obj.get("_nonAnchoringIdsBackingStore"))
        anchor_entity_id = from_union([from_str, from_none], obj.get("anchorEntityId"))
        archived = from_union([AuditStamp.from_dict, from_none], obj.get("archived"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created = from_union([AuditStamp.from_dict, from_none], obj.get("created"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        detail = from_union([KnowledgeCardDetail.from_dict, from_none], obj.get("detail"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        hashtags = from_union([lambda x: from_list(Hashtag.from_dict, x), from_none], obj.get("hashtags"))
        knowledge_card_info_id = from_union([from_str, from_none], obj.get("id"))
        last_modified = from_union([AuditStamp.from_dict, from_none], obj.get("lastModified"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        related_entity_ids = from_union([lambda x: from_list(from_str, x), from_none], obj.get("relatedEntityIds"))
        return KnowledgeCardInfo(id, non_anchoring_ids_backing_store, anchor_entity_id, archived, aspect_type, created, created_at, detail, entity_id, hashtags, knowledge_card_info_id, last_modified, latest, related_entity_ids)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["_nonAnchoringIdsBackingStore"] = from_union([lambda x: from_list(from_str, x), from_none], self.non_anchoring_ids_backing_store)
        result["anchorEntityId"] = from_union([from_str, from_none], self.anchor_entity_id)
        result["archived"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.archived)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["created"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.created)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["detail"] = from_union([lambda x: to_class(KnowledgeCardDetail, x), from_none], self.detail)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["hashtags"] = from_union([lambda x: from_list(lambda x: to_class(Hashtag, x), x), from_none], self.hashtags)
        result["id"] = from_union([from_str, from_none], self.knowledge_card_info_id)
        result["lastModified"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.last_modified)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["relatedEntityIds"] = from_union([lambda x: from_list(from_str, x), from_none], self.related_entity_ids)
        return result


@dataclass
class ValidationConfirmation:
    confirmed_by: Optional[AuditStamp] = None
    knowledge_card_id: Optional[str] = None
    message: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ValidationConfirmation':
        assert isinstance(obj, dict)
        confirmed_by = from_union([AuditStamp.from_dict, from_none], obj.get("confirmedBy"))
        knowledge_card_id = from_union([from_str, from_none], obj.get("knowledgeCardId"))
        message = from_union([from_str, from_none], obj.get("message"))
        return ValidationConfirmation(confirmed_by, knowledge_card_id, message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["confirmedBy"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.confirmed_by)
        result["knowledgeCardId"] = from_union([from_str, from_none], self.knowledge_card_id)
        result["message"] = from_union([from_str, from_none], self.message)
        return result


@dataclass
class ValidationRequest:
    knowledge_card_id: Optional[str] = None
    message: Optional[str] = None
    recipient_id: Optional[str] = None
    requested_by: Optional[AuditStamp] = None
    requester_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ValidationRequest':
        assert isinstance(obj, dict)
        knowledge_card_id = from_union([from_str, from_none], obj.get("knowledgeCardId"))
        message = from_union([from_str, from_none], obj.get("message"))
        recipient_id = from_union([from_str, from_none], obj.get("recipientId"))
        requested_by = from_union([AuditStamp.from_dict, from_none], obj.get("requestedBy"))
        requester_id = from_union([from_str, from_none], obj.get("requesterId"))
        return ValidationRequest(knowledge_card_id, message, recipient_id, requested_by, requester_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["knowledgeCardId"] = from_union([from_str, from_none], self.knowledge_card_id)
        result["message"] = from_union([from_str, from_none], self.message)
        result["recipientId"] = from_union([from_str, from_none], self.recipient_id)
        result["requestedBy"] = from_union([lambda x: to_class(AuditStamp, x), from_none], self.requested_by)
        result["requesterId"] = from_union([from_str, from_none], self.requester_id)
        return result


@dataclass
class KnowledgeCardValidation:
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    confirmation: Optional[ValidationConfirmation] = None
    created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    knowledge_card_validation_id: Optional[str] = None
    latest: Optional[bool] = None
    request: Optional[ValidationRequest] = None

    @staticmethod
    def from_dict(obj: Any) -> 'KnowledgeCardValidation':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        confirmation = from_union([ValidationConfirmation.from_dict, from_none], obj.get("confirmation"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        knowledge_card_validation_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        request = from_union([ValidationRequest.from_dict, from_none], obj.get("request"))
        return KnowledgeCardValidation(id, aspect_type, confirmation, created_at, entity_id, knowledge_card_validation_id, latest, request)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["confirmation"] = from_union([lambda x: to_class(ValidationConfirmation, x), from_none], self.confirmation)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.knowledge_card_validation_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["request"] = from_union([lambda x: to_class(ValidationRequest, x), from_none], self.request)
        return result


@dataclass
class KnowledgeCardLogicalID:
    """Implemented in {@link KnowledgeCard} output type
    Definite assignment assertion is safe since it is defined in output subtype.
    This is due to unresolved TypeScript bug preventing this class from being defined as an
    abstract class, and
    then being used in a mixin {@see https://github.com/microsoft/TypeScript/issues/37142}
    """
    id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'KnowledgeCardLogicalID':
        assert isinstance(obj, dict)
        id = from_union([from_str, from_none], obj.get("id"))
        return KnowledgeCardLogicalID(id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_union([from_str, from_none], self.id)
        return result


@dataclass
class KnowledgeCard:
    """Backing store for an optionally provided creation date"""
    created_at: Optional[datetime] = None
    """A class representation of the BSON ObjectId type."""
    id: Optional[ObjectID] = None
    knowledge_card_created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    entity_type: Optional[EntityType] = None
    """A getter for the id property that's directly generated from the
    entity type & logical ID.
    """
    knowledge_card_id: Optional[str] = None
    knowledge_card_info: Optional[KnowledgeCardInfo] = None
    knowledge_card_validation: Optional[KnowledgeCardValidation] = None
    last_modified_at: Optional[datetime] = None
    """Implemented in {@link KnowledgeCard} output type
    Definite assignment assertion is safe since it is defined in output subtype.
    This is due to unresolved TypeScript bug preventing this class from being defined as an
    abstract class, and
    then being used in a mixin {@see https://github.com/microsoft/TypeScript/issues/37142}
    """
    logical_id: Optional[KnowledgeCardLogicalID] = None

    @staticmethod
    def from_dict(obj: Any) -> 'KnowledgeCard':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        knowledge_card_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        deleted_at = from_union([from_datetime, from_none], obj.get("deletedAt"))
        entity_type = from_union([EntityType, from_none], obj.get("entityType"))
        knowledge_card_id = from_union([from_str, from_none], obj.get("id"))
        knowledge_card_info = from_union([KnowledgeCardInfo.from_dict, from_none], obj.get("knowledgeCardInfo"))
        knowledge_card_validation = from_union([KnowledgeCardValidation.from_dict, from_none], obj.get("knowledgeCardValidation"))
        last_modified_at = from_union([from_datetime, from_none], obj.get("lastModifiedAt"))
        logical_id = from_union([KnowledgeCardLogicalID.from_dict, from_none], obj.get("logicalId"))
        return KnowledgeCard(created_at, id, knowledge_card_created_at, deleted_at, entity_type, knowledge_card_id, knowledge_card_info, knowledge_card_validation, last_modified_at, logical_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.knowledge_card_created_at)
        result["deletedAt"] = from_union([lambda x: x.isoformat(), from_none], self.deleted_at)
        result["entityType"] = from_union([lambda x: to_enum(EntityType, x), from_none], self.entity_type)
        result["id"] = from_union([from_str, from_none], self.knowledge_card_id)
        result["knowledgeCardInfo"] = from_union([lambda x: to_class(KnowledgeCardInfo, x), from_none], self.knowledge_card_info)
        result["knowledgeCardValidation"] = from_union([lambda x: to_class(KnowledgeCardValidation, x), from_none], self.knowledge_card_validation)
        result["lastModifiedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_modified_at)
        result["logicalId"] = from_union([lambda x: to_class(KnowledgeCardLogicalID, x), from_none], self.logical_id)
        return result


@dataclass
class ViewedEntityHistory:
    date: Optional[datetime] = None
    entity_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ViewedEntityHistory':
        assert isinstance(obj, dict)
        date = from_union([from_datetime, from_none], obj.get("date"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        return ViewedEntityHistory(date, entity_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["date"] = from_union([lambda x: x.isoformat(), from_none], self.date)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        return result


@dataclass
class PersonActivity:
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    person_activity_id: Optional[str] = None
    latest: Optional[bool] = None
    recently_viewed_history: Optional[List[ViewedEntityHistory]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonActivity':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        person_activity_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        recently_viewed_history = from_union([lambda x: from_list(ViewedEntityHistory.from_dict, x), from_none], obj.get("recentlyViewedHistory"))
        return PersonActivity(id, aspect_type, created_at, entity_id, person_activity_id, latest, recently_viewed_history)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.person_activity_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["recentlyViewedHistory"] = from_union([lambda x: from_list(lambda x: to_class(ViewedEntityHistory, x), x), from_none], self.recently_viewed_history)
        return result


@dataclass
class Input:
    created: Optional[datetime] = None
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Input':
        assert isinstance(obj, dict)
        created = from_union([from_datetime, from_none], obj.get("created"))
        name = from_union([from_str, from_none], obj.get("name"))
        return Input(created, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["created"] = from_union([lambda x: x.isoformat(), from_none], self.created)
        result["name"] = from_union([from_str, from_none], self.name)
        return result


@dataclass
class PersonEditableInfo:
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    entity_id: Optional[str] = None
    person_editable_info_id: Optional[str] = None
    latest: Optional[bool] = None
    skills: Optional[List[Input]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonEditableInfo':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        person_editable_info_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        skills = from_union([lambda x: from_list(Input.from_dict, x), from_none], obj.get("skills"))
        return PersonEditableInfo(id, aspect_type, created_at, entity_id, person_editable_info_id, latest, skills)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.person_editable_info_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["skills"] = from_union([lambda x: from_list(lambda x: to_class(Input, x), x), from_none], self.skills)
        return result


@dataclass
class PersonLogicalID:
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    email: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonLogicalID':
        assert isinstance(obj, dict)
        email = from_union([from_str, from_none], obj.get("email"))
        return PersonLogicalID(email)

    def to_dict(self) -> dict:
        result: dict = {}
        result["email"] = from_union([from_str, from_none], self.email)
        return result


@dataclass
class GroupID:
    group_name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'GroupID':
        assert isinstance(obj, dict)
        group_name = from_union([from_str, from_none], obj.get("groupName"))
        return GroupID(group_name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["groupName"] = from_union([from_str, from_none], self.group_name)
        return result


@dataclass
class PersonOrganization:
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    department: Optional[str] = None
    division: Optional[str] = None
    employee_number: Optional[str] = None
    entity_id: Optional[str] = None
    groups: Optional[List[GroupID]] = None
    person_organization_id: Optional[str] = None
    latest: Optional[bool] = None
    manager: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonOrganization':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        department = from_union([from_str, from_none], obj.get("department"))
        division = from_union([from_str, from_none], obj.get("division"))
        employee_number = from_union([from_str, from_none], obj.get("employeeNumber"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        groups = from_union([lambda x: from_list(GroupID.from_dict, x), from_none], obj.get("groups"))
        person_organization_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        manager = from_union([from_str, from_none], obj.get("manager"))
        name = from_union([from_str, from_none], obj.get("name"))
        title = from_union([from_str, from_none], obj.get("title"))
        return PersonOrganization(id, aspect_type, created_at, department, division, employee_number, entity_id, groups, person_organization_id, latest, manager, name, title)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["department"] = from_union([from_str, from_none], self.department)
        result["division"] = from_union([from_str, from_none], self.division)
        result["employeeNumber"] = from_union([from_str, from_none], self.employee_number)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["groups"] = from_union([lambda x: from_list(lambda x: to_class(GroupID, x), x), from_none], self.groups)
        result["id"] = from_union([from_str, from_none], self.person_organization_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["manager"] = from_union([from_str, from_none], self.manager)
        result["name"] = from_union([from_str, from_none], self.name)
        result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class PersonProperties:
    """Object / output type for PersonProperties aspect contains the full aspect fields
    
    Input type for PersonProperties aspect, contains just the common fields across input and
    output
    """
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    display_name: Optional[str] = None
    entity_id: Optional[str] = None
    first_name: Optional[str] = None
    full_name: Optional[str] = None
    person_properties_id: Optional[str] = None
    issuer: Optional[str] = None
    last_login: Optional[str] = None
    last_name: Optional[str] = None
    latest: Optional[bool] = None
    mobile_phone: Optional[str] = None
    occupation: Optional[str] = None
    primary_phone: Optional[str] = None
    provider_name: Optional[str] = None
    status: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonProperties':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        avatar_url = from_union([from_str, from_none], obj.get("avatarUrl"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        display_name = from_union([from_str, from_none], obj.get("displayName"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        first_name = from_union([from_str, from_none], obj.get("firstName"))
        full_name = from_union([from_str, from_none], obj.get("fullName"))
        person_properties_id = from_union([from_str, from_none], obj.get("id"))
        issuer = from_union([from_str, from_none], obj.get("issuer"))
        last_login = from_union([from_str, from_none], obj.get("lastLogin"))
        last_name = from_union([from_str, from_none], obj.get("lastName"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        mobile_phone = from_union([from_str, from_none], obj.get("mobilePhone"))
        occupation = from_union([from_str, from_none], obj.get("occupation"))
        primary_phone = from_union([from_str, from_none], obj.get("primaryPhone"))
        provider_name = from_union([from_str, from_none], obj.get("providerName"))
        status = from_union([from_str, from_none], obj.get("status"))
        return PersonProperties(id, aspect_type, avatar_url, created_at, display_name, entity_id, first_name, full_name, person_properties_id, issuer, last_login, last_name, latest, mobile_phone, occupation, primary_phone, provider_name, status)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["avatarUrl"] = from_union([from_str, from_none], self.avatar_url)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["displayName"] = from_union([from_str, from_none], self.display_name)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["firstName"] = from_union([from_str, from_none], self.first_name)
        result["fullName"] = from_union([from_str, from_none], self.full_name)
        result["id"] = from_union([from_str, from_none], self.person_properties_id)
        result["issuer"] = from_union([from_str, from_none], self.issuer)
        result["lastLogin"] = from_union([from_str, from_none], self.last_login)
        result["lastName"] = from_union([from_str, from_none], self.last_name)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["mobilePhone"] = from_union([from_str, from_none], self.mobile_phone)
        result["occupation"] = from_union([from_str, from_none], self.occupation)
        result["primaryPhone"] = from_union([from_str, from_none], self.primary_phone)
        result["providerName"] = from_union([from_str, from_none], self.provider_name)
        result["status"] = from_union([from_str, from_none], self.status)
        return result


@dataclass
class PersonSlackProfile:
    id: Optional[ObjectID] = None
    aspect_type: Optional[AspectType] = None
    created_at: Optional[datetime] = None
    deleted: Optional[bool] = None
    entity_id: Optional[str] = None
    person_slack_profile_id: Optional[str] = None
    latest: Optional[bool] = None
    slack_id: Optional[str] = None
    team_id: Optional[str] = None
    username: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PersonSlackProfile':
        assert isinstance(obj, dict)
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        aspect_type = from_union([AspectType, from_none], obj.get("aspectType"))
        created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        deleted = from_union([from_bool, from_none], obj.get("deleted"))
        entity_id = from_union([from_str, from_none], obj.get("entityId"))
        person_slack_profile_id = from_union([from_str, from_none], obj.get("id"))
        latest = from_union([from_bool, from_none], obj.get("latest"))
        slack_id = from_union([from_str, from_none], obj.get("slackId"))
        team_id = from_union([from_str, from_none], obj.get("teamId"))
        username = from_union([from_str, from_none], obj.get("username"))
        return PersonSlackProfile(id, aspect_type, created_at, deleted, entity_id, person_slack_profile_id, latest, slack_id, team_id, username)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["aspectType"] = from_union([lambda x: to_enum(AspectType, x), from_none], self.aspect_type)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["deleted"] = from_union([from_bool, from_none], self.deleted)
        result["entityId"] = from_union([from_str, from_none], self.entity_id)
        result["id"] = from_union([from_str, from_none], self.person_slack_profile_id)
        result["latest"] = from_union([from_bool, from_none], self.latest)
        result["slackId"] = from_union([from_str, from_none], self.slack_id)
        result["teamId"] = from_union([from_str, from_none], self.team_id)
        result["username"] = from_union([from_str, from_none], self.username)
        return result


@dataclass
class Person:
    """A person entity represents any individual who is a member of the organization (or beyond)
    and can
    potentially have some relation to the other entities in our application
    """
    """Backing store for an optionally provided creation date"""
    created_at: Optional[datetime] = None
    """A class representation of the BSON ObjectId type."""
    id: Optional[ObjectID] = None
    activity: Optional[PersonActivity] = None
    person_created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    editable_info: Optional[PersonEditableInfo] = None
    entity_type: Optional[EntityType] = None
    """A getter for the id property that's directly generated from the
    entity type & logical ID.
    """
    person_id: Optional[str] = None
    last_modified_at: Optional[datetime] = None
    """Identify an entity "logically".
    Each entity must have a logicalId to be ingested.
    A compelling use-case is that this allows a producer to create an
    instance of the Entity without requiring an entity ID to be
    obtained prior to instantiation, potentially resulting in two round-trips
    """
    logical_id: Optional[PersonLogicalID] = None
    organization: Optional[PersonOrganization] = None
    password: Optional[str] = None
    properties: Optional[PersonProperties] = None
    slack_profile: Optional[PersonSlackProfile] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Person':
        assert isinstance(obj, dict)
        created_at = from_union([from_datetime, from_none], obj.get("_createdAt"))
        id = from_union([ObjectID.from_dict, from_none], obj.get("_id"))
        activity = from_union([PersonActivity.from_dict, from_none], obj.get("activity"))
        person_created_at = from_union([from_datetime, from_none], obj.get("createdAt"))
        deleted_at = from_union([from_datetime, from_none], obj.get("deletedAt"))
        editable_info = from_union([PersonEditableInfo.from_dict, from_none], obj.get("editableInfo"))
        entity_type = from_union([EntityType, from_none], obj.get("entityType"))
        person_id = from_union([from_str, from_none], obj.get("id"))
        last_modified_at = from_union([from_datetime, from_none], obj.get("lastModifiedAt"))
        logical_id = from_union([PersonLogicalID.from_dict, from_none], obj.get("logicalId"))
        organization = from_union([PersonOrganization.from_dict, from_none], obj.get("organization"))
        password = from_union([from_str, from_none], obj.get("password"))
        properties = from_union([PersonProperties.from_dict, from_none], obj.get("properties"))
        slack_profile = from_union([PersonSlackProfile.from_dict, from_none], obj.get("slackProfile"))
        return Person(created_at, id, activity, person_created_at, deleted_at, editable_info, entity_type, person_id, last_modified_at, logical_id, organization, password, properties, slack_profile)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["_id"] = from_union([lambda x: to_class(ObjectID, x), from_none], self.id)
        result["activity"] = from_union([lambda x: to_class(PersonActivity, x), from_none], self.activity)
        result["createdAt"] = from_union([lambda x: x.isoformat(), from_none], self.person_created_at)
        result["deletedAt"] = from_union([lambda x: x.isoformat(), from_none], self.deleted_at)
        result["editableInfo"] = from_union([lambda x: to_class(PersonEditableInfo, x), from_none], self.editable_info)
        result["entityType"] = from_union([lambda x: to_enum(EntityType, x), from_none], self.entity_type)
        result["id"] = from_union([from_str, from_none], self.person_id)
        result["lastModifiedAt"] = from_union([lambda x: x.isoformat(), from_none], self.last_modified_at)
        result["logicalId"] = from_union([lambda x: to_class(PersonLogicalID, x), from_none], self.logical_id)
        result["organization"] = from_union([lambda x: to_class(PersonOrganization, x), from_none], self.organization)
        result["password"] = from_union([from_str, from_none], self.password)
        result["properties"] = from_union([lambda x: to_class(PersonProperties, x), from_none], self.properties)
        result["slackProfile"] = from_union([lambda x: to_class(PersonSlackProfile, x), from_none], self.slack_profile)
        return result


@dataclass
class MetadataChangeEvent:
    dashboard: Optional[Dashboard] = None
    dataset: Optional[Dataset] = None
    event_header: Optional[EventHeader] = None
    knowledge_card: Optional[KnowledgeCard] = None
    """A person entity represents any individual who is a member of the organization (or beyond)
    and can
    potentially have some relation to the other entities in our application
    """
    person: Optional[Person] = None

    @staticmethod
    def from_dict(obj: Any) -> 'MetadataChangeEvent':
        assert isinstance(obj, dict)
        dashboard = from_union([Dashboard.from_dict, from_none], obj.get("dashboard"))
        dataset = from_union([Dataset.from_dict, from_none], obj.get("dataset"))
        event_header = from_union([EventHeader.from_dict, from_none], obj.get("eventHeader"))
        knowledge_card = from_union([KnowledgeCard.from_dict, from_none], obj.get("knowledgeCard"))
        person = from_union([Person.from_dict, from_none], obj.get("person"))
        return MetadataChangeEvent(dashboard, dataset, event_header, knowledge_card, person)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dashboard"] = from_union([lambda x: to_class(Dashboard, x), from_none], self.dashboard)
        result["dataset"] = from_union([lambda x: to_class(Dataset, x), from_none], self.dataset)
        result["eventHeader"] = from_union([lambda x: to_class(EventHeader, x), from_none], self.event_header)
        result["knowledgeCard"] = from_union([lambda x: to_class(KnowledgeCard, x), from_none], self.knowledge_card)
        result["person"] = from_union([lambda x: to_class(Person, x), from_none], self.person)
        return result


def metadata_change_event_from_dict(s: Any) -> MetadataChangeEvent:
    return MetadataChangeEvent.from_dict(s)


def metadata_change_event_to_dict(x: MetadataChangeEvent) -> Any:
    return to_class(MetadataChangeEvent, x)
