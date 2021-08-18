import logging
from typing import Dict, List, Optional, Text, Union

import convo.shared.data
from convo.shared.core.training_data.structures import StoryPlot
from convo.shared.importers import utils
from convo.shared.importers import autoconfig
from convo.shared.importers.importer import TrainingDataImporter
from convo.shared.importers.autoconfig import TrainingClassification
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.core.domain import InvalidDomain, Domain
import convo.shared.utils.io

log = logging.getLogger(__name__)


class FileImporter(TrainingDataImporter):
    """Default `TrainingFileImporter` implementation."""

    def __init__(
        self,
        config_file: Optional[Text] = None,
        domain_path: Optional[Text] = None,
        training_data_paths: Optional[Union[List[Text], Text]] = None,
        training_type: Optional[TrainingClassification] = TrainingClassification.TWO,
    ):

        self._domain_path = domain_path

        self._nlu_files = convo.shared.data.get_all_data_files(
            training_data_paths, convo.shared.data.nlu_file_check
        )
        self._story_files = convo.shared.data.get_all_data_files(
            training_data_paths, convo.shared.data.story_file_check
        )

        self.config = autoconfig.get_config(config_file, training_type)

    async def get_config(self) -> Dict:
        return self.config

    async def fetch_stories(
        self,
        template_variables: Optional[Dict] = None,
        use_e2e: bool = False,
        exclusion_percentage: Optional[int] = None,
    ) -> StoryPlot:

        return await utils.story_graph_from_path(
            self._story_files,
            await self.domain(),
            template_variables,
            use_e2e,
            exclusion_percentage,
        )

    async def fetch_nlu_data(self, language: Optional[Text] = "en") -> TrainingDataSet:
        return utils.training_dataset_from_paths(self._nlu_files, language)

    async def domain(self) -> Domain:
        domain_name = Domain.empty()

        # If domain path is None, return an empty domain
        if not self._domain_path:
            return domain_name
        try:
            domain_name = Domain.load(self._domain_path)
            domain_name.missing_templates_check()
        except InvalidDomain as e:
            convo.shared.utils.io.raising_warning(
                f"Loading domain from '{self._domain_path}' failed. Using "
                f"empty domain. Error: '{e}'"
            )

        return domain_name
