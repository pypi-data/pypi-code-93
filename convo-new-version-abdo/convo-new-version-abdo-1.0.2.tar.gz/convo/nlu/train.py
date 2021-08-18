import logging
import typing
from typing import Any, Optional, Text, Tuple, Union, Dict

import convo.shared.utils.common
import convo.utils.common as common_utils
from convo.nlu import config, utils
from convo.nlu.components import ElementBuilder
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.model import Interpreter, Instructor
from convo.shared.nlu.training_data.loading import load_data_set
from convo.utils import io as io_utils
from convo.utils.endpoints import EndpointConfiguration


if typing.TYPE_CHECKING:
    from convo.shared.importers.importer import TrainingDataImporter
    from convo.shared.nlu.training_data.training_data import TrainingDataSet

log = logging.getLogger(__name__)


class ExceptionTraining(Exception):
    """Exception wrapping lower level exceptions that may happen while training

    Attributes:
        failed_target_project -- name of the failed project
        message -- explanation of why the request is invalid
    """

    def __init__(
        self,
        failed_target_project: Optional[Text] = None,
        exception: Optional[Exception] = None,
    ) -> None:
        self.failed_target_project = failed_target_project
        if exception:
            self.message = exception.args[0]
        else:
            self.message = ""
        super(ExceptionTraining, self).__init__()

    def __str__(self) -> Text:
        return self.message


async def loading_dataset_from_end_point(
    data_endpoint: EndpointConfiguration, language: Optional[Text] = "en"
) -> "TrainingDataSet":
    """Load training data from a URL."""
    import requests

    if not utils.is_url(data_endpoint.url):
        raise requests.exceptions.InvalidURL(data_endpoint.url)
    try:
        resp = await data_endpoint.request("get")
        resp.raise_for_status()
        temporary_data_file = io_utils.create_temp_file(resp.content, mode="w+b")
        training_dataset = load_data_set(temporary_data_file, language)

        return training_dataset
    except Exception as e:
        log.warning(f"Could not retrieve training data from URL:\n{e}")


def persistor_creation(persistor: Optional[Text]):
    """Create a remote persistor to store the model if configured."""

    if persistor is not None:
        from convo.nlu.persistor import fetch_persistor

        return fetch_persistor(persistor)
    else:
        return None


async def training(
    nlu_configuration: Union[Text, Dict, ConvoNLUModelConfiguration],
    data: Union[Text, "TrainingDataImporter"],
    path: Optional[Text] = None,
    fixed_model_name: Optional[Text] = None,
    storage: Optional[Text] = None,
    component_builder: Optional[ElementBuilder] = None,
    training_data_endpoint: Optional[EndpointConfiguration] = None,
    persist_nlu_training_data: bool = False,
    **kwargs: Any,
) -> Tuple[Instructor, Interpreter, Optional[Text]]:
    """Loads the trainer and the data and runs the training of the model."""
    from convo.shared.importers.importer import TrainingDataImporter

    if not isinstance(nlu_configuration, ConvoNLUModelConfiguration):
        nlu_configuration = config.load(nlu_configuration)

    # Ensure we are training a model that we can save in the end
    # WARN: there is still a race condition if a model with the same name is
    # trained in another subprocess
    instructor = Instructor(nlu_configuration, component_builder)
    persisto_name = persistor_creation(storage)
    if training_data_endpoint is not None:
        training_dataset = await loading_dataset_from_end_point(
            training_data_endpoint, nlu_configuration.language
        )
    elif isinstance(data, TrainingDataImporter):
        training_dataset = await data.fetch_nlu_data(nlu_configuration.language)
    else:
        training_dataset = load_data_set(data, nlu_configuration.language)

    training_dataset.print_statistics()
    if training_dataset.used_entity_roles_groups():
        convo.shared.utils.common.mark_experimental_feature(
            "Entity Roles and Groups feature"
        )

    fetch_interpreter = instructor.train(training_dataset, **kwargs)

    if path:
        persistance_path = instructor.persist(
            path, persisto_name, fixed_model_name, persist_nlu_training_data
        )
    else:
        persistance_path = None

    return instructor, fetch_interpreter, persistance_path
