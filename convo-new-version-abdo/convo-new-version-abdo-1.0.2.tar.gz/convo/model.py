import copy
import glob
import hashlib
import logging
import os
import shutil
from subprocess import CalledProcessError, DEVNULL, check_output  # skipcq:BAN-B404
import tempfile
import typing
from pathlib import Path
from typing import Text, Tuple, Union, Optional, List, Dict, NamedTuple

import convo.shared.utils.io
import convo.utils.io
from convo.cli.utils import generate_output_path
from convo.shared.utils.cli import printing_success
from convo.shared.constants import (
    CONFIGURATION_KEYS_CORE,
    CONFIGURATION_KEYS_NLU ,
    CONFIGURATION_KEYS,
    CONVO_DEFAULT_DOMAIN_PATH,
    DEFAULT_MODEL_PATH ,
    DEFAULT_CORE_SUB_DIRECTORY_NAME,
    DEFAULT_NLU_SUB_DIRECTORY_NAME,
)

from convo.core.utils import get_dict_hash
from convo.exceptions import ModelNotPresent
from convo.utils.common import TempDirPath

if typing.TYPE_CHECKING:
    from convo.shared.importers.importer import TrainingDataImporter


logger = logging.getLogger(__name__)


# Type alias for the fingerprint
Fingerprint = Dict[Text, Union[Text, List[Text], int, float]]

FINGER_PRINT_FILE_PATH_FLOW = "fingerprint.json"

FINGER_PRINT_CONFIGURATION_KEY = "config"
FINGER_PRINT_CONFIGURATION_CORE_KEY = "core-config"
FINGER_PRINT_CONFIGURATION_NLU_KEY = "nlu-config"
FINGER_PRINT_DOMAIN_EXCLUDE_NLG_KEY = "domain"
FINGER_PRINT_NLG_KEY = "nlg"
FINGER_PRINT_VERS_KEY = "version"
FINGER_PRINT_STORY_KEY = "stories"
FINGER_PRINT_NLU_DATA_SET_KEY = "messages"
FINGER_PRINT_PROJ = "project"
FINGERPRINT_TRAINED_AT_KEY = "trained_at"


class Sec(NamedTuple):
    """Defines relevant fingerprint sections which are used to decide whether a model
    should be retrained."""

    name: Text
    important_keys: List[Text]


SEC_CORE = Sec(
    name="Core model",
    important_keys=[
        FINGER_PRINT_CONFIGURATION_KEY,
        FINGER_PRINT_CONFIGURATION_CORE_KEY,
        FINGER_PRINT_DOMAIN_EXCLUDE_NLG_KEY,
        FINGER_PRINT_STORY_KEY,
        FINGER_PRINT_VERS_KEY,
    ],
)
SEC_NLU = Sec(
    name="NLU model",
    important_keys=[
        FINGER_PRINT_CONFIGURATION_KEY,
        FINGER_PRINT_CONFIGURATION_NLU_KEY,
        FINGER_PRINT_NLU_DATA_SET_KEY,
        FINGER_PRINT_VERS_KEY,
    ],
)
SEC_NLG = Sec(name="NLG templates", important_keys=[FINGER_PRINT_NLG_KEY])


class FingerprintComparisonResult:
    def __init__(
        self,
        nlu: bool = True,
        core: bool = True,
        nlg: bool = True,
        force_training: bool = False,
    ):
        """Creates a `FingerprintComparisonResult` instance.

        Args:
            nlu: `True` if the NLU model should be retrained.
            core: `True` if the Core model should be retrained.
            nlg: `True` if the responses in the domain should be updated.
            force_training: `True` if a training of all parts is forced.
        """
        self.nlu = nlu
        self.core = core
        self.nlg = nlg
        self.force_training = force_training

    def is_supervising_required(self) -> bool:
        """Check if anything has to be retrained."""

        return any([self.nlg, self.nlu, self.core, self.force_training])

    def should_resupervise_core(self) -> bool:
        """Check if the Core model has to be updated."""

        return self.force_training or self.core

    def should_resupervise_nlg(self) -> bool:
        """Check if the responses have to be updated."""

        return self.should_resupervise_core() or self.nlg

    def should_resupervise_nlu(self) -> bool:
        """Check if the NLU model has to be updated."""

        return self.force_training or self.nlu


def fetch_model(model_path: Text = DEFAULT_MODEL_PATH ) -> TempDirPath:
    """Get a model and unpack it. Raises a `ModelNotPresent` exception if
    no model could be found at the provided path.

    Args:
        model_path: Path to the zipped model. If it's a dir, the latest
                    trained model is returned.

    Returns:
        Path to the unpacked model.

    """
    if not model_path:
        raise ModelNotPresent("No path specified.")
    elif not os.path.exists(model_path):
        raise ModelNotPresent(f"No file or dir at '{model_path}'.")

    if os.path.isdir(model_path):
        model_path = fetch_latest_model(model_path)
        if not model_path:
            raise ModelNotPresent(
                f"Could not find any Convo model files in '{model_path}'."
            )
    elif not model_path.endswith(".tar.gz"):
        raise ModelNotPresent(f"Path '{model_path}' does not point to a Convo model file.")

    return unpacking_model(model_path)


def fetch_latest_model(model_path: Text = DEFAULT_MODEL_PATH ) -> Optional[Text]:
    """Get the latest model from a path.

    Args:
        model_path: Path to a dir containing zipped models.

    Returns:
        Path to latest model in the given dir.

    """
    if not os.path.exists(model_path) or os.path.isfile(model_path):
        model_path = os.path.dirname(model_path)

    list_of_files = glob.glob(os.path.join(model_path, "*.tar.gz"))

    if len(list_of_files) == 0:
        return None

    return max(list_of_files, key=os.path.getctime)


def unpacking_model(
    model_file: Text, working_directory: Optional[Union[Path, Text]] = None
) -> TempDirPath:
    """Unpack a zipped Convo model.

    Args:
        model_file: Path to zipped model.
        working_directory: Location where the model should be unpacked to.
                           If `None` a temporary dir will be created.

    Returns:
        Path to unpacked Convo model.

    """
    import tarfile

    if working_directory is None:
        working_directory = tempfile.mkdtemp()

    # All files are in a subdirectory.
    try:
        with tarfile.open(model_file, mode="r:gz") as tar:
            tar.extractall(working_directory)
            logger.debug(f"Extracted model to '{working_directory}'.")
    except Exception as e:
        logger.error(f"Failed to extract model at {model_file}. Error: {e}")
        raise

    return TempDirPath(working_directory)


def fetch_model_subdirectories(
    unpacked_model_path: Text,
) -> Tuple[Optional[Text], Optional[Text]]:
    """Return convo_paths for Core and NLU model directories, if they exist.
    If neither directories exist, a `ModelNotPresent` exception is raised.

    Args:
        unpacked_model_path: Path to unpacked Convo model.

    Returns:
        Tuple (path to Core subdirectory if it exists or `None` otherwise,
               path to NLU subdirectory if it exists or `None` otherwise).

    """
    core_path_flow = os.path.join(unpacked_model_path, DEFAULT_CORE_SUB_DIRECTORY_NAME)
    nlu_path_flow = os.path.join(unpacked_model_path, DEFAULT_NLU_SUB_DIRECTORY_NAME)

    if not os.path.isdir(core_path_flow):
        core_path_flow = None

    if not os.path.isdir(nlu_path_flow):
        nlu_path_flow = None

    if not core_path_flow and not nlu_path_flow:
        raise ModelNotPresent(
            "No NLU or Core data for unpacked model at: '{}'.".format(
                unpacked_model_path
            )
        )

    return core_path_flow, nlu_path_flow


def create_pack(
    training_directory: Text,
    output_filename: Text,
    fingerprint: Optional[Fingerprint] = None,
) -> Text:
    """Create a zipped Convo model from trained model files.

    Args:
        training_directory: Path to the dir which contains the trained
                            model files.
        output_filename: Name of the zipped model file to be created.
        fingerprint: A unique fingerprint to identify the model version.

    Returns:
        Path to zipped model.

    """
    import tarfile

    if fingerprint:
        persist_finger_print(training_directory, fingerprint)

    output_directory = os.path.dirname(output_filename)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with tarfile.open(output_filename, "w:gz") as tar:
        for elem in os.scandir(training_directory):
            tar.add(elem.path, arcname=elem.name)

    shutil.rmtree(training_directory)
    return output_filename


def proj_finger_print() -> Optional[Text]:
    """Create a hash for the project in the current working directory.

    Returns:
        project hash
    """
    try:
        distant = check_output(  # skipcq:BAN-B607,BAN-B603
            ["git", "remote", "get-url", "origin"], stderr=DEVNULL
        )
        return hashlib.sha256(distant).hexdigest()
    except (CalledProcessError, OSError):
        return None


async def model_finger_print(file_importer: "TrainingDataImporter") -> Fingerprint:
    """Create a model fingerprint from its used configuration and training data.

    Args:
        file_importer: File importer which provides the training data and model config.

    Returns:
        The fingerprint.

    """
    import time

    CONFIGURATION = await file_importer.get_config()
    domain_name = await file_importer.domain()
    story = await file_importer.fetch_stories()
    nlu_data_set = await file_importer.fetch_nlu_data()

    outcomes = domain_name.templates

    # Do a copy of the domain to not change the actual domain (shallow is enough)
    domain_name = copy.copy(domain_name)
    # don't include the response texts in the fingerprint.
    # Their fingerprint is separate.
    domain_name.templates = []

    return {
        FINGER_PRINT_CONFIGURATION_KEY: _get_hash_of_configuration(CONFIGURATION, exclude_keys=CONFIGURATION_KEYS),
        FINGER_PRINT_CONFIGURATION_CORE_KEY: _get_hash_of_configuration(
            CONFIGURATION, include_keys=CONFIGURATION_KEYS_CORE
        ),
        FINGER_PRINT_CONFIGURATION_NLU_KEY: _get_hash_of_configuration(
            CONFIGURATION, include_keys=CONFIGURATION_KEYS_NLU
        ),
        FINGER_PRINT_DOMAIN_EXCLUDE_NLG_KEY: hash(domain_name),
        FINGER_PRINT_NLG_KEY: get_dict_hash(outcomes),
        FINGER_PRINT_PROJ: proj_finger_print(),
        FINGER_PRINT_NLU_DATA_SET_KEY: hash(nlu_data_set),
        FINGER_PRINT_STORY_KEY: hash(story),
        FINGERPRINT_TRAINED_AT_KEY: time.time(),
        FINGER_PRINT_VERS_KEY: convo.__version__,  # pytype: disable=module-attr
    }


def _get_hash_of_configuration(
    config: Optional[Dict],
    include_keys: Optional[List[Text]] = None,
    exclude_keys: Optional[List[Text]] = None,
) -> Text:
    if not config:
        return ""

    keys = include_keys or list(filter(lambda k: k not in exclude_keys, config.keys()))

    sub_config = {k: config[k] for k in keys if k in config}

    return get_dict_hash(sub_config)


def finger_print_from_path_flow(model_path: Text) -> Fingerprint:
    """Load a persisted fingerprint.

    Args:
        model_path: Path to dir containing the fingerprint.

    Returns:
        The fingerprint or an empty dict if no fingerprint was found.
    """
    if not model_path or not os.path.exists(model_path):
        return {}

    fingerprint_path = os.path.join(model_path, FINGER_PRINT_FILE_PATH_FLOW)

    if os.path.isfile(fingerprint_path):
        return convo.shared.utils.io.reading_json_file(fingerprint_path)
    else:
        return {}


def persist_finger_print(output_path: Text, fingerprint: Fingerprint):
    """Persist a model fingerprint.

    Args:
        output_path: Directory in which the fingerprint should be saved.
        fingerprint: The fingerprint to be persisted.

    """

    path_flow = os.path.join(output_path, FINGER_PRINT_FILE_PATH_FLOW)
    convo.shared.utils.io.dump_object_as_json_to_file(path_flow, fingerprint)


def did_sec_finger_print_change(
    fingerprint1: Fingerprint, fingerprint2: Fingerprint, section: Sec
) -> bool:
    """Check whether the fingerprint of a section has changed."""
    for k in section.important_keys:
        if fingerprint1.get(k) != fingerprint2.get(k):
            logger.info(f"Data ({k}) for {section.name} section changed.")
            return True
    return False


def move_model_data(source: Text, target: Text) -> bool:
    """Move two model directories.

    Args:
        source: The original folder which should be merged in another.
        target: The destination folder where it should be moved to.

    Returns:
        `True` if the merge was successful, else `False`.

    """
    try:
        shutil.move(source, target)
        return True
    except Exception as e:
        logging.debug(f"Could not merge model: {e}")
        return False


def should_retrain(
    new_fingerprint: Fingerprint, old_model: Text, train_path: Text
) -> FingerprintComparisonResult:
    """Check which components of a model should be retrained.

    Args:
        new_fingerprint: The fingerprint of the new model to be trained.
        old_model: Path to the old zipped model file.
        train_path: Path to the dir in which the new model will be trained.

    Returns:
        A FingerprintComparisonResult object indicating whether Convo Core and/or Convo NLU needs
        to be retrained or not.

    """
    fingerprint_comparison = FingerprintComparisonResult()

    if old_model is None or not os.path.exists(old_model):
        return fingerprint_comparison

    with unpacking_model(old_model) as unpacked:
        last_fingerprint = finger_print_from_path_flow(unpacked)
        old_core, old_nlu = fetch_model_subdirectories(unpacked)

        fingerprint_comparison = FingerprintComparisonResult(
            core=did_sec_finger_print_change(
                last_fingerprint, new_fingerprint, SEC_CORE
            ),
            nlu=did_sec_finger_print_change(
                last_fingerprint, new_fingerprint, SEC_NLU
            ),
            nlg=did_sec_finger_print_change(
                last_fingerprint, new_fingerprint, SEC_NLG
            ),
        )

        core_merge_failed = False
        if not fingerprint_comparison.should_resupervise_core():
            target_path = os.path.join(train_path, DEFAULT_CORE_SUB_DIRECTORY_NAME)
            core_merge_failed = not move_model_data(old_core, target_path)
            fingerprint_comparison.core = core_merge_failed

        if not fingerprint_comparison.should_resupervise_nlg() and core_merge_failed:
            # If moving the Core model failed, we should also retrain NLG
            fingerprint_comparison.nlg = True

        if not fingerprint_comparison.should_resupervise_nlu():
            target_path = os.path.join(train_path, "nlu")
            fingerprint_comparison.nlu = not move_model_data(old_nlu, target_path)

        return fingerprint_comparison


def pack_model(
    fingerprint: Fingerprint,
    output_directory: Text,
    train_path: Text,
    fixed_model_name: Optional[Text] = None,
    model_prefix: Text = "",
) -> Text:
    """
    Compress a trained model.

    Args:
        fingerprint: fingerprint of the model
        output_directory: path to the dir in which the model should be stored
        train_path: path to uncompressed model
        fixed_model_name: name of the compressed model file
        model_prefix: prefix of the compressed model file

    Returns: path to 'tar.gz' model file
    """
    output_directory = generate_output_path(
        output_directory, prefix=model_prefix, fixed_name=fixed_model_name
    )
    create_pack(train_path, output_directory, fingerprint)

    printing_success(
        "Your Convo model is trained and saved at '{}'.".format(
            os.path.abspath(output_directory)
        )
    )

    return output_directory


async def upgrade_model_with_new_domain(
    importer: "TrainingDataImporter", unpacked_model_path: Union[Path, Text]
) -> None:
    """Overwrites the domain of an unpacked model with a new domain.

    Args:
        importer: Importer which provides the new domain.
        unpacked_model_path: Path to the unpacked model.
    """

    model_path = Path(unpacked_model_path) / DEFAULT_CORE_SUB_DIRECTORY_NAME
    domain = await importer.domain()

    domain.persist(model_path / CONVO_DEFAULT_DOMAIN_PATH)
