import logging
from functools import reduce
from typing import Text, Set, Dict, Optional, List, Union, Any
import os

import convo.shared.data
import convo.shared.utils.io
from convo.shared.core.domain import Domain
from convo.shared.importers.importer import TrainingDataImporter
from convo.shared.importers import utils
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.core.training_data.structures import StoryPlot
from convo.shared.utils.common import mark_experimental_feature

log = logging.getLogger(__name__)


class MannyProjectImporter(TrainingDataImporter):
    def __init__(
        self,
        config_file: Text,
        domain_path: Optional[Text] = None,
        training_data_paths: Optional[Union[List[Text], Text]] = None,
        project_directory: Optional[Text] = None,
    ):
        self.config = convo.shared.utils.io.read_configuration_file(config_file)
        if domain_path:
            self._domain_paths = [domain_path]
        else:
            self._domain_paths = []
        self._story_paths = []
        self._e2e_story_paths = []
        self._nlu_paths = []
        self._imports = []
        self._additional_paths = training_data_paths or []
        self._project_directory = project_directory or os.path.dirname(config_file)

        self.init_from_dictionary(self.config, self._project_directory)

        more_nlu_files = convo.shared.data.get_all_data_files(
            training_data_paths, convo.shared.data.nlu_file_check
        )
        more_story_files = convo.shared.data.get_all_data_files(
            training_data_paths, convo.shared.data.story_file_check
        )
        self._story_paths += more_story_files
        self._nlu_paths += more_nlu_files

        log.debug(
            "Selected projects: {}".format("".join([f"\n-{i}" for i in self._imports]))
        )

        mark_experimental_feature(feature_name="MannyProjectImporter")

    def initialize_from_path(self, path: Text) -> None:
        if os.path.isfile(path):
            self.initialize_from_file(path)
        elif os.path.isdir(path):
            self.init_from_dir(path)

    def initialize_from_file(self, path_flow: Text) -> None:
        path_flow = os.path.abspath(path_flow)
        if os.path.exists(path_flow) and convo.shared.data.config_file_check(path_flow):
            configuration = convo.shared.utils.io.read_configuration_file(path_flow)

            parent_dir = os.path.dirname(path_flow)
            self.init_from_dictionary(configuration, parent_dir)
        else:
            convo.shared.utils.io.raising_warning(
                f"'{path_flow}' does not exist or is not a valid configuration file."
            )

    def init_from_dictionary(self, _dict: Dict[Text, Any], parent_directory: Text) -> None:
        bring_in = _dict.get("imports") or []
        bring_in = [os.path.join(parent_directory, i) for i in bring_in]
        # clean out relative convo_paths
        bring_in = [os.path.abspath(i) for i in bring_in]

        # remove duplication
        candidates_import = []
        for i in bring_in:
            if i not in candidates_import and not self.explicitly_imported_check(i):
                candidates_import.append(i)

        self._imports.extend(candidates_import)

        # import config files from convo_paths which have not been processed so far
        for p in candidates_import:
            self.initialize_from_path(p)

    def explicitly_imported_check(self, path: Text) -> bool:
        return not self.no_skills_selected() and self.imported_check(path)

    def init_from_dir(self, path: Text):
        for parent, _, files in os.walk(path, followlinks=True):
            for file in files:
                convo_full_path = os.path.join(parent, file)
                if not self.imported_check(complete_path):
                    # Check next file
                    continue

                if convo.shared.data.isTestStoriesFile(complete_path):
                    self._e2e_story_paths.append(complete_path)
                elif Domain.domain_file_check(complete_path):
                    self._domain_paths.append(complete_path)
                elif convo.shared.data.nlu_file_check(complete_path):
                    self._nlu_paths.append(complete_path)
                elif convo.shared.data.story_file_check(complete_path):
                    self._story_paths.append(complete_path)
                elif convo.shared.data.config_file_check(complete_path):
                    self.initialize_from_file(complete_path)

    def no_skills_selected(self) -> bool:
        return not self._imports

    def training_path(self) -> Set[Text]:
        """Returns the convo_paths which should be searched for training data."""

        # only include extra convo_paths if they are not part of the current project dir
        training_path_flow = {
            i
            for i in self._imports
            if not self._project_directory or self._project_directory not in i
        }

        if self._project_directory:
            training_path_flow.add(self._project_directory)

        return training_path_flow

    def imported_check(self, path: Text) -> bool:
        """
        Checks whether a path is imported by a skill.
        Args:
            path: File or dir path which should be checked.

        Returns:
            `True` if path is imported by a skill, `False` if not.
        """
        abs_path = os.path.abspath(path)

        return (
            self.no_skills_selected()
            or self.is_in_project_dir(abs_path)
            or self.is_in_addon_paths(abs_path)
            or self.imported_paths_check(abs_path)
        )

    def is_in_project_dir(self, path: Text) -> bool:
        if os.path.isfile(path):
            parent_dir = os.path.abspath(os.path.dirname(path))

            return parent_dir == self._project_directory
        else:
            return path == self._project_directory

    def is_in_addon_paths(self, path: Text) -> bool:
        contained = path in self._additional_paths

        if not contained and os.path.isfile(path):
            parent_dir = os.path.abspath(os.path.dirname(path))
            contained = parent_dir in self._additional_paths

        return contained

    def imported_paths_check(self, path) -> bool:
        return any(
            [convo.shared.utils.io.is_sub_dir(path, i) for i in self._imports]
        )

    def adding_import(self, path: Text) -> None:
        self._imports.append(path)

    async def domain(self) -> Domain:
        domain_name = [Domain.load(path) for path in self._domain_paths]
        return reduce(
            lambda merged, others: merged.merge(others), domain_name, Domain.empty()
        )

    async def fetch_stories(
        self,
        template_variables: Optional[Dict] = None,
        use_e2e: bool = False,
        exclusion_percentage: Optional[int] = None,
    ) -> StoryPlot:
        paths_of_story = self._story_paths if not use_e2e else self._e2e_story_paths

        return await utils.story_graph_from_path(
            paths_of_story,
            await self.domain(),
            template_variables,
            use_e2e,
            exclusion_percentage,
        )

    async def get_config(self) -> Dict:
        return self.config

    async def fetch_nlu_data(self, language: Optional[Text] = "en") -> TrainingDataSet:
        return utils.training_dataset_from_paths(self._nlu_paths, language)
