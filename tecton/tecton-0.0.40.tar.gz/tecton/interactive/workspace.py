from typing import List
from typing import Optional
from typing import Union

import tecton
from tecton import conf
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.display import Displayable
from tecton._internals.sdk_decorators import documented_by
from tecton._internals.sdk_decorators import sdk_public_method
from tecton._internals.utils import is_materializable_workspace
from tecton.interactive.dataset import Dataset
from tecton.interactive.feature_table import FeatureTable
from tecton.interactive.feature_view import FeatureView
from tecton.interactive.new_transformation import NewTransformation
from tecton.interactive.transformation import Transformation
from tecton_proto.metadataservice.metadata_service_pb2 import ListWorkspacesRequest


class Workspace:
    """
    Workspace class.

    This class represents a Workspace. The Workspace class is used to fetch Tecton Primitives, which are stored in a Workspace.
    """

    def __init__(
        self, workspace: str, _automatic_materialization_enabled: Optional[bool] = None, _validate: bool = True
    ):
        """
        Fetch an existing :class:`Workspace` by name.

        :param workspace: Workspace name.
        """
        self.workspace = workspace

        if _automatic_materialization_enabled is None:
            self.automatic_materialization_enabled = is_materializable_workspace(self.workspace)
        else:
            self.automatic_materialization_enabled = _automatic_materialization_enabled

        if _validate:
            self._validate()

    def _validate(self):
        request = ListWorkspacesRequest()
        response = metadata_service.instance().ListWorkspaces(request)

        workspace_from_resp = None
        for ws in response.workspaces:
            if ws.name == self.workspace:
                workspace_from_resp = ws
                break

        if workspace_from_resp is None:
            raise errors.NONEXISTENT_WORKSPACE(workspace, workspaces)

        if ws.capabilities.materializable != self.automatic_materialization_enabled:
            raise errors.INCORRECT_MATERIALIZATION_ENABLED_FLAG(
                self.automatic_materialization_enabled, ws.capabilities.materializable
            )

    @classmethod
    @sdk_public_method
    def get_all(self) -> List["Workspace"]:
        """
        Returns a list of all registered Workspaces.

        :return: A list of Workspace objects.
        """
        request = ListWorkspacesRequest()
        response = metadata_service.instance().ListWorkspaces(request)
        workspaces = [
            Workspace(ws.name, _automatic_materialization_enabled=ws.capabilities.materializable, _validate=False)
            for ws in response.workspaces
        ]

        # Return materialization enabled workspaces first (alphabetical), then workspaces without materialization enabled.
        return sorted(workspaces, key=lambda ws: (not ws.automatic_materialization_enabled, ws.workspace))

    def __enter__(self):
        self.previous_workspace = conf.get_or_none("TECTON_WORKSPACE")
        conf.set("TECTON_WORKSPACE", self.workspace)

    def __exit__(self, type, value, traceback):
        conf.set("TECTON_WORKSPACE", self.previous_workspace)

    def __repr__(self) -> str:
        capability_str = (
            "Automatic Materialization Enabled"
            if self.automatic_materialization_enabled
            else "Automatic Materialization Disabled"
        )
        return f"{self.workspace} ({capability_str})"

    @sdk_public_method
    def summary(self) -> Displayable:
        from texttable import Texttable

        items = [
            ("Workspace Name", self.workspace),
            ("Automatic Materialization Enabled", "True" if self.automatic_materialization_enabled else "False"),
        ]
        return Displayable.from_items(
            headings=["", ""], items=items, deco=(Texttable.BORDER | Texttable.VLINES | Texttable.HLINES)
        )

    @classmethod
    @sdk_public_method
    def get(cls, name) -> "Workspace":
        """
        Fetch an existing :class:`Workspace` by name.

        :param name: Workspace name.
        """
        return Workspace(name)

    @sdk_public_method
    def get_feature_package(self, name: str):
        """
        Returns a :class:`FeaturePackage` within a workspace.

        :param name: FeaturePackage name.
        :return: the named FeaturePackage
        """

        return tecton.get_feature_package(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_feature_view(self, name: str) -> FeatureView:
        """
        Returns a :class:`FeatureView` within a workspace.

        :param name: FeatureView name
        :return: the named FeatureView
        """
        return tecton.get_feature_view(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_feature_table(self, name: str) -> FeatureTable:
        """
        Returns a :class:`FeatureTable` within a workspace.

        :param name: FeatureTable name
        :return: the named FeatureTable
        """
        return tecton.get_feature_table(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_feature_service(self, name: str):
        """
        Returns a :class:`FeatureService` within a workspace.

        :param name: FeatureService name.
        :return: the named FeatureService
        """

        return tecton.get_feature_service(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_data_source(self, name: str):
        """
        Returns a :class:`BatchDataSource` or :class:`StreamDataSource` within a workspace.

        :param name: BatchDataSource or StreamDataSource name.
        :return: the named BatchDataSource or StreamDataSource
        """

        return tecton.get_data_source(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_virtual_data_source(self, name: str):
        """
        Returns a :class:`VirtualDataSource` within a workspace.

        :param name: VirtualDataSource name.
        :return: the named VirtualDataSource
        """

        return tecton.get_virtual_data_source(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_entity(self, name: str):
        """
        Returns an :class:`Entity` within a workspace.

        :param name: Entity name.
        :return: the named Entity
        """

        return tecton.get_entity(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_transformation(self, name: str) -> Union[Transformation, NewTransformation]:
        """
        Returns a :class:`Transformation` within a workspace.

        :param name: Transformation name.
        :return: the named Transformation
        """

        return tecton.get_transformation(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_new_transformation(self, name: str) -> NewTransformation:
        """
        Returns a :class:`NewTransformation` within a workspace.

        :param name: Transformation name.
        :return: the named Transformation
        """

        return tecton.get_new_transformation(name, workspace_name=self.workspace)

    @sdk_public_method
    def get_dataset(self, name) -> Dataset:
        """
        Returns a :class:`Dataset` within a workspace.

        :param name: Dataset name.
        :return: the named Dataset
        """
        return tecton.get_dataset(name, workspace_name=self.workspace)

    @sdk_public_method
    def list_datasets(self) -> List[str]:
        """
        Returns a list of all registered Datasets within a workspace.

        :return: A list of strings.
        """
        return tecton.list_datasets(workspace_name=self.workspace)

    @sdk_public_method
    def list_feature_packages(self) -> List[str]:
        """
        Returns a list of all registered FeaturePackages within a workspace.

        :return: A list of strings.
        """
        return tecton.list_feature_packages(workspace_name=self.workspace)

    @sdk_public_method
    def list_feature_views(self) -> List[str]:
        """
        Returns a list of all registered FeatureViews within a workspace.

        :return: A list of strings.
        """
        return tecton.list_feature_views(workspace_name=self.workspace)

    @sdk_public_method
    def list_feature_services(self) -> List[str]:
        """
        Returns a list of all registered FeatureServices within a workspace.

        :return: A list of strings.
        """
        return tecton.list_feature_services(workspace_name=self.workspace)

    @sdk_public_method
    def list_transformations(self) -> List[str]:
        """
        Returns a list of all registered Transformations within a workspace.

        :return: A list of strings.
        """
        return tecton.list_transformations(workspace_name=self.workspace)

    @sdk_public_method
    def list_new_transformations(self) -> List[str]:
        """
        Returns a list of all registered Transformations within a workspace.

        :return: A list of strings.
        """
        return tecton.list_new_transformations(workspace_name=self.workspace)

    @sdk_public_method
    def list_entities(self) -> List[str]:
        """
        Returns a list of all registered Entities within a workspace.

        :returns: A list of strings.
        """
        return tecton.list_entities(workspace_name=self.workspace)

    @sdk_public_method
    def list_virtual_data_sources(self) -> List[str]:
        """
        Returns a list of all registered VirtualDataSources within a workspace.

        :return: A list of strings.
        """
        return tecton.list_virtual_data_sources(workspace_name=self.workspace)

    @sdk_public_method
    def list_data_sources(self) -> List[str]:
        """
        Returns a list of all registered DataSources within a workspace.

        :return: A list of strings.
        """
        return tecton.list_data_sources(workspace_name=self.workspace)

    @sdk_public_method
    def list_feature_tables(self) -> List[str]:
        """
        Returns a list of all registered FeatureTables within a workspace.

        :return: A list of strings.
        """
        return tecton.list_feature_tables(workspace_name=self.workspace)


@documented_by(Workspace.get)
@sdk_public_method
def get_workspace(name: str):
    return Workspace.get(name)
