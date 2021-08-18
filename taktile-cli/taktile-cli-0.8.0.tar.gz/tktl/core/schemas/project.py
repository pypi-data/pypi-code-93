from typing import List, Optional, Union

from pydantic import BaseModel

from tktl.core.t import InstanceTypeT, ProjectAssetSourceT, ProjectAssetT


class ProjectContentsBase(BaseModel):
    type: str
    name: str
    path: str


class ProjectFile(ProjectContentsBase):
    type: str = "file"


class ProjectFileWithContent(ProjectContentsBase):
    type: str = "file"
    content: str


class ProjectDirectory(ProjectContentsBase):
    type: str = "dir"


class ProjectAsset(ProjectContentsBase):
    calculated_sha: str
    kind: ProjectAssetT
    source: ProjectAssetSourceT
    requires_download: bool


class RestServiceConfigSchema(BaseModel):
    replicas: int
    max_replicas: int
    instance_type: InstanceTypeT


class ArrowServiceConfigSchema(BaseModel):
    replicas: int
    instance_type: InstanceTypeT


class TktlServiceConfigSchema(BaseModel):
    rest: RestServiceConfigSchema
    arrow: ArrowServiceConfigSchema


class TktlYamlConfigSchema(BaseModel):

    """
    deployment_prefix?: master
    service:

      rest:
        instance_type: gp.small
        replicas: 1
        max_replicas: 1

      arrow:
        instance_type: gp.small
        replicas: 1

    version: version
    """

    deployment_prefix: Optional[str]
    service: TktlServiceConfigSchema
    version: str


class TktlYamlConfigValidationError(BaseModel):
    loc: str
    msg: str


class ProjectValidationOutput(BaseModel):
    title: str
    summary: str
    text: str


ProjectContentSingleItemT = Union[ProjectFile, ProjectDirectory]
ProjectContentMultiItemT = List[ProjectContentSingleItemT]
ProjectContentT = Union[
    ProjectContentSingleItemT, ProjectContentMultiItemT, ProjectFileWithContent
]
