from typing import List
from typing import Union

import tecton
from tecton import conf
from tecton._internals import errors
from tecton._internals.display import Displayable
from tecton._internals.sdk_decorators import documented_by
from tecton._internals.sdk_decorators import sdk_public_method
from tecton._internals.utils import is_materializable_workspace
from tecton.fco_listers import list_workspaces
from tecton.interactive.dataset import Dataset
from tecton.interactive.feature_table import FeatureTable
from tecton.interactive.feature_view import FeatureView
from tecton.interactive.new_transformation import NewTransformation
from tecton.interactive.transformation import Transformation


class Workspace:
    """
    Workspace class.

    This class represents a Workspace. The Workspace class is used to fetch Tecton Primitives, which are stored in a Workspace.
    """

    def __init__(self, workspace: str):
        """
        Fetch an existing :class:`Workspace` by name.

        :param workspace: Workspace name.
        """
        workspaces = list_workspaces()
        if workspace not in workspaces:
            raise errors.NONEXISTENT_WORKSPACE(workspace, workspaces)
        self.workspace = workspace

    def __enter__(self):
        self.previous_workspace = conf.get_or_none("TECTON_WORKSPACE")
        conf.set("TECTON_WORKSPACE", self.workspace)

    def __exit__(self, type, value, traceback):
        conf.set("TECTON_WORKSPACE", self.previous_workspace)

    @sdk_public_method
    def summary(self) -> Displayable:
        from texttable import Texttable

        items = [
            ("Workspace Name", self.workspace),
            ("Automatic Materialization Enabled", "True" if is_materializable_workspace(self.workspace) else "False"),
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
