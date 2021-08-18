from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MediaType(str, Enum):
    CSV = 'text/csv'
    GEOJSON = 'application/geo+json'
    JSON = 'application/json'


class DatasetType(str, Enum):
    MANAGED = 'managed'
    EXTERNALLY_HOSTED = 'externally-hosted'
    VECTOR_TILE = 'vector-tile'
    RASTER_TILE = 'raster-tile'
    HEX_TILE = 'hex-tile'
    SQL = 'sql'


class DatasetMetadata(BaseModel):
    """A model representing metadata for an Unfolded Studio Dataset"""

    content_type: Optional[str] = Field(alias='contentType')
    size: Optional[int]
    source: Optional[str]
    tileset_data_url: Optional[str] = Field(alias='tilesetDataUrl')
    tileset_metadata_url: Optional[str] = Field(alias='tilesetMetadataUrl')
    image_url: Optional[str] = Field(alias='imageUrl')
    metadata_url: Optional[str] = Field(alias='metadataUrl')
    data_status: Optional[str] = Field(alias='dataStatus')

    class Config:
        allow_population_by_field_name = True


class Dataset(BaseModel):
    """A model representing an Unfolded Studio Dataset"""

    id: UUID
    name: str
    type: DatasetType
    created_at: datetime = Field(..., alias='createdAt')
    updated_at: datetime = Field(..., alias='updatedAt')
    description: Optional[str]
    is_valid: bool = Field(..., alias='isValid')
    metadata: DatasetMetadata

    class Config:
        allow_population_by_field_name = True


class MapState(BaseModel):
    """A model representing an Unfolded Studio Map Starte"""

    id: UUID
    # data contains the actual map configuration, and should be modeled more concretely than a
    # generic Dictionary.
    # Todo (wesam@unfolded.ai): revisit this once we have a style building strategy
    data: Dict

    class Config:
        allow_population_by_field_name = True


class MapUpdateParams(BaseModel):
    """A model respresenting creation and update parameters for Unfolded Maps"""

    name: Optional[str]
    description: Optional[str]
    latest_state: Optional[MapState] = Field(None, alias="latestState")
    datasets: Optional[List[UUID]]

    class Config:
        allow_population_by_field_name = True


class Map(BaseModel):
    """A model representing an Unfolded Studio Map"""

    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime = Field(..., alias='createdAt')
    updated_at: datetime = Field(..., alias='updatedAt')
    latest_state: Optional[MapState] = Field(None, alias="latestState")
    datasets: Optional[List[Dataset]]

    class Config:
        allow_population_by_field_name = True
